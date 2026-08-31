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
"""
import copy

from django.conf import settings
from django.utils.module_loading import import_string

DEFAULT_REAL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


def _is_allowed(address, allowed_domains, allowed_addresses):
    address = (address or '').strip().lower()
    if not address:
        return True  # nothing to protect against an empty recipient slot
    if address in allowed_addresses:
        return True
    domain = address.rsplit('@', 1)[-1] if '@' in address else ''
    return bool(domain) and domain in allowed_domains


class AllowlistEmailBackend:
    """Wraps another EMAIL_BACKEND, redirecting non-allowlisted mail."""

    def __init__(self, fail_silently=False, **kwargs):
        real_backend_path = getattr(
            settings, 'SAFE_EMAIL_REAL_BACKEND', DEFAULT_REAL_BACKEND
        )
        real_backend_cls = import_string(real_backend_path)
        self.real_backend = real_backend_cls(fail_silently=fail_silently, **kwargs)
        self.fail_silently = fail_silently

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
        recipients = list(message.to) + list(message.cc) + list(message.bcc)
        if all(_is_allowed(r, self.allowed_domains, self.allowed_addresses) for r in recipients):
            return message

        if not self.redirect_to:
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
        redirected.subject = '[STAGING, would have gone to: {}] {}'.format(
            original_recipients, message.subject
        )
        redirect_note = (
            '\n\n---\n[Redirected by AllowlistEmailBackend -- this message was '
            'addressed to: {}]\n'.format(original_recipients)
        )
        redirected.body = (message.body or '') + redirect_note
        return redirected
