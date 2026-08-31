"""Allowlist/redirect email backend for non-production environments.

Any environment whose database might be (or become) a copy of production
data holds real users' real email addresses. Without this backend, that
environment's normal Django mail-sending code (password resets, gift
notices, campaign emails, etc.) would deliver real email to real people --
exactly what happened on test.unglue.it 2026-08-31 after its database was
refreshed from a prod snapshot (see regluit#1238).

Enabled by setting ``EMAIL_SAFE_MODE=true`` (see settings/common.py, which
then points ``EMAIL_BACKEND`` at ``AllowlistEmailBackend`` below). Wraps
whatever the real backend would otherwise have been and, for each outgoing
message:

- lets it through unchanged if every recipient (To/Cc/Bcc) is on the
  allowlist (``EMAIL_SAFE_MODE_ALLOWED_DOMAINS`` / ``_ADDRESSES``);
- otherwise redirects the *whole* message to
  ``EMAIL_SAFE_MODE_REDIRECT_TO``, with the original recipients recorded in
  the subject and appended to the body, so a tester can still see what
  *would* have gone out;
- refuses to send (raises, rather than silently dropping or silently
  delivering to an unknown address) if a message needs redirecting but no
  ``EMAIL_SAFE_MODE_REDIRECT_TO`` is configured.

Silent dropping is deliberately not an option here -- it's exactly the kind
of behavior that made two earlier staging-email incidents (regluit#1164,
regluit-provisioning#22) more confusing to diagnose than they needed to be:
"nothing happened" looks identical to "it's broken" and to "it's working
correctly," and no one incident is more common than the others.

Deploying this to an actual box (setting EMAIL_SAFE_MODE=true + an
allowlist/redirect address in its environment, for both the web process AND
Celery) is a separate, provisioning-side step -- not done by this module
existing in the codebase. See regluit#1238.
"""
import copy
import logging
import os
from email.utils import parseaddr

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.utils.module_loading import import_string

logger = logging.getLogger(__name__)

DEFAULT_REAL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
ALLOWLIST_BACKEND_PATH = 'regluit.utils.safe_email_backend.AllowlistEmailBackend'


def resolve_email_backend(email_safe_mode, current_backend, env=None):
    """Decide what EMAIL_BACKEND (and, when active, what real backend to
    wrap) a settings module should use, given whether EMAIL_SAFE_MODE is on.

    Pulled out as a plain function -- not inlined in settings/common.py --
    specifically so it's directly unit-testable. Django's test runner
    (setup_test_environment) unconditionally overwrites settings.EMAIL_BACKEND
    with the locmem backend before any TestCase body runs, which means a
    test that imports django.conf.settings and checks EMAIL_BACKEND from
    inside a TestCase can never actually observe what settings/common.py
    computed -- an assertion like that would pass even if this logic were
    broken (CC review, 2026-08-31, on the first version of this file that
    inlined the conditional directly in common.py). Testing this function
    directly, with no settings module or test runner involved, avoids that
    trap entirely.

    Returns (real_backend_to_wrap, effective_email_backend).
    """
    if env is None:
        env = os.environ
    if not email_safe_mode:
        return current_backend, current_backend
    real_backend = env.get('SAFE_EMAIL_REAL_BACKEND', current_backend)
    return real_backend, ALLOWLIST_BACKEND_PATH


def _bare_address(address):
    """Extract the bare address from an optional 'Display Name <addr>' form."""
    _, addr = parseaddr(address or '')
    return addr


def _is_allowed(address, allowed_domains, allowed_addresses):
    address = _bare_address(address).strip().lower()
    if not address:
        return True  # nothing to protect against an empty recipient slot
    if address in allowed_addresses:
        return True
    domain = address.rsplit('@', 1)[-1] if '@' in address else ''
    return bool(domain) and domain in allowed_domains


class AllowlistEmailBackend(BaseEmailBackend):
    """Wraps another EMAIL_BACKEND, redirecting non-allowlisted mail.

    Subclasses Django's BaseEmailBackend (not a bare object) so it supports
    everything the real interface promises, including use as a context
    manager (`with get_connection() as conn: ...`) -- caught missing in CC
    review, 2026-08-31.
    """

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        real_backend_path = getattr(
            settings, 'SAFE_EMAIL_REAL_BACKEND', DEFAULT_REAL_BACKEND
        )
        real_backend_cls = import_string(real_backend_path)
        self.real_backend = real_backend_cls(fail_silently=fail_silently, **kwargs)

        self.allowed_domains = {
            d.strip().lower()
            for d in getattr(settings, 'EMAIL_SAFE_MODE_ALLOWED_DOMAINS', '').split(',')
            if d.strip()
        }
        self.allowed_addresses = {
            a.strip().lower()
            for a in getattr(settings, 'EMAIL_SAFE_MODE_ALLOWED_ADDRESSES', '').split(',')
            if a.strip()
        }
        self.redirect_to = getattr(settings, 'EMAIL_SAFE_MODE_REDIRECT_TO', '') or None

    def open(self):
        return self.real_backend.open()

    def close(self):
        return self.real_backend.close()

    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        prepared = [self._redirect_if_needed(m) for m in email_messages]
        return self.real_backend.send_messages(prepared)

    def _redirect_if_needed(self, message):
        # message.recipients() -- not message.to/.cc/.bcc directly -- is
        # Django's own authoritative list of who a message actually goes
        # to; a message subclass can override it to include recipients
        # that never appear in .to/.cc/.bcc at all. Checking .to/.cc/.bcc
        # would miss those (CC review, 2026-08-31).
        recipients = list(message.recipients())
        if all(_is_allowed(r, self.allowed_domains, self.allowed_addresses) for r in recipients):
            return message

        if not self.redirect_to:
            logger.error(
                "AllowlistEmailBackend: refusing to send a message to %r -- "
                "not fully allowlisted and no EMAIL_SAFE_MODE_REDIRECT_TO "
                "configured. Logged at ERROR (not just raised) because "
                "Celery's send_mail_task swallows exceptions from backends "
                "without re-raising, which would otherwise make this look "
                "like a silently dropped email.",
                recipients,
            )
            raise RuntimeError(
                "AllowlistEmailBackend: message to {!r} is not fully "
                "allowlisted (EMAIL_SAFE_MODE_ALLOWED_DOMAINS/_ADDRESSES) "
                "and EMAIL_SAFE_MODE_REDIRECT_TO is not set, so there's "
                "nowhere safe to send it. Refusing to send rather than "
                "guess.".format(recipients)
            )

        redirected = copy.copy(message)
        original_recipients = ', '.join(recipients) if recipients else '(no recipients)'
        redirected.to = [self.redirect_to]
        redirected.cc = []
        redirected.bcc = []
        # Deliberately generic subject -- subjects are far more likely than
        # bodies to end up in SMTP logs, mailbox indexing, or downstream
        # notifications, so the original recipients (real PII once a box
        # holds a prod DB copy) go in the body only (CC review, 2026-08-31).
        redirected.subject = '[STAGING - redirected by AllowlistEmailBackend] {}'.format(
            message.subject
        )
        redirect_note = (
            '\n\n---\n[Redirected by AllowlistEmailBackend -- this message was '
            'addressed to: {}]\n'.format(original_recipients)
        )
        redirected.body = (message.body or '') + redirect_note

        # Belt-and-suspenders: if message.recipients() is overridden in a
        # way that setting .to/.cc/.bcc doesn't actually change, refuse to
        # send rather than assume the rewrite worked (CC review,
        # 2026-08-31).
        actual = list(redirected.recipients())
        if actual != [self.redirect_to]:
            raise RuntimeError(
                "AllowlistEmailBackend: rewriting recipients to the "
                "redirect target didn't take effect (message.recipients() "
                "still returns {!r}) -- this message type can't be safely "
                "redirected. Refusing to send.".format(actual)
            )
        return redirected
