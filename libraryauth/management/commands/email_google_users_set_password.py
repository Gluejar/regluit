"""Pre-removal "set a password" email for Google-only accounts (#1237).

Context: #1237 removes the "Sign in with Google" button. A prod query
(2026-08-31, read-only, counts only -- see PR #1237 comment) found 8,457
Google-auth accounts with no usable password (149 active in the last 90
days), all with an email address on file. Removing the button without first
giving these accounts a way to set a password would strand anyone who
relies on it. This command is that "give them a way" step: it finds the
affected accounts and (only when explicitly told to) emails each one a
link to unglue.it's existing "forgot your password?" flow
(``libraryauth_password_reset``, ``libraryauth.forms.SocialAwarePasswordResetForm``
-- already accepts users with no usable password, no new view/token logic
needed here).

Safety, by design, at three independent layers:

1. **Dry run is the default.** Without ``--send`` this command only ever
   prints who it *would* email -- COUNT/subset by default, full list with
   ``--verbose-list`` -- and sends nothing.
2. **``--send`` alone is still a no-op.** It additionally requires the
   environment variable named by ``SEND_ENV_VAR`` (see below) to be set to
   a truthy value. This is a deliberate two-key switch: a reviewer or a
   future cron invocation that passes ``--send`` by habit/mistake still
   can't send unless someone has separately opted the *environment* in.
   Per this session's brief: "No sending of any email, no deploys, no prod
   DB access" -- this command was authored and tested with ``--send``
   never actually engaged.
3. **``EMAIL_SAFE_MODE`` (regluit#1239) is the safety net underneath both
   of the above.** On any non-prod box with ``EMAIL_SAFE_MODE=true`` set,
   Django's real send is wrapped by
   ``regluit.utils.safe_email_backend.AllowlistEmailBackend``, which
   redirects anything not addressed to an allowlisted domain/address. That
   makes it safe to rehearse this command's ``--send`` path against a real
   (prod-copy) staging database -- on production, where EMAIL_SAFE_MODE is
   never set, mail sends for real, which is exactly why gates 1 and 2
   exist.

The email copy in ``registration/google_set_password_email*.txt`` is
DRAFT COPY -- Raymond will rewrite it before this ever ships for real.

Failure handling (Codex round-1 review, 2026-09-02): a single bad
recipient (malformed address, etc.) is logged and the run continues --
useful with thousands of legacy addresses. But a *systemic* problem
(unreachable SMTP host, a broken template, misconfigured mail settings)
must not be treated the same way, silently working through the whole
candidate list and reporting "SUCCESS." So: the mail connection is opened
once, up front (a connection failure aborts immediately, before contacting
anyone); the first candidate's context is rendered once as a preflight
check (a broken template also aborts before anyone is contacted); if
``--max-consecutive-failures`` isolated failures happen in a row (default
5), the run aborts rather than grinding through thousands of doomed sends;
and any unresolved failure makes the command exit non-zero
(``CommandError``) -- a monitoring/cron consumer should not see exit 0
read as "all clear."

Restart-safety (Codex rounds 1 and 2): there is no persistent
"already emailed" ledger. ``--after-id ID`` skips every candidate with
id <= ID, letting an interrupted run resume without a new DB table --
but (round-2 finding) because isolated failures don't stop the run,
resuming past a run that had *any* failures can silently skip retrying
those specific ids: an id cursor can't represent holes. So this command
prints every failed id at the end of a ``--send`` run and is explicit
that ``--after-id`` only guarantees "not reprocessed," never "already
succeeded" -- failed ids in that list need a separate, deliberate retry
(e.g. a follow-up run with no ``--after-id`` and a tight ``--limit``, or
a future ``--retry-ids`` option). A real unattended bulk campaign would
still want a durable delivery ledger; still out of scope here, see
REPORT.
"""
import argparse
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import get_connection, send_mail
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from django.urls import reverse

# Both providers seen on prod for the Google backend (PR #1237 comment,
# 2026-08-31): the live 'google-oauth2' (social_core.backends.google) and a
# legacy 'google' provider from an older integration. A user can in
# principle have rows under either or both -- .distinct() below collapses
# that to one email per person.
GOOGLE_PROVIDERS = ('google-oauth2', 'google')

# Two-key switch, gate 2 of 3 described in the module docstring above.
# --send alone does nothing without this also being set in the process
# environment.
SEND_ENV_VAR = 'REGLUIT_ALLOW_SET_PASSWORD_EMAIL_SEND'

SUBJECT_TEMPLATE = 'registration/google_set_password_email_subject.txt'
BODY_TEMPLATE = 'registration/google_set_password_email.txt'

DEFAULT_MAX_CONSECUTIVE_FAILURES = 5


def _non_negative_int(value):
    """argparse type= validator. Plain int() would silently accept negative
    values, and Python list slicing treats a negative --limit as "all but
    the last N" rather than rejecting it (Codex round-1 review, 2026-09-02,
    reproduced: --limit -1 against 8,457 candidates processes 8,456 of
    them) -- exactly backwards from what an operator asking for a small,
    safe batch would expect.

    Note this only guards the command-line parsing path. Django's
    call_command() applies type= to string CLI-style args but NOT to
    already-typed keyword arguments (Codex round-2 review, 2026-09-02,
    reproduced: call_command(..., limit=-1) bypasses this entirely) -- see
    the explicit re-check in Command.handle() below for the path this
    function can't cover.
    """
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError(
            "must be a non-negative integer, got %r" % value
        )
    return ivalue


def _require_non_negative(option_name, value):
    """Re-validate a --limit/--after-id/--max-consecutive-failures-shaped
    option inside handle() itself, not just via argparse's type=. Closes
    the call_command(**kwargs) bypass described in _non_negative_int's
    docstring -- a caller invoking this command programmatically with a
    negative int never goes through argparse parsing at all.
    """
    if value is not None and value < 0:
        raise CommandError(
            "%s must be a non-negative integer, got %r" % (option_name, value)
        )


def find_candidates(providers=GOOGLE_PROVIDERS, after_id=None):
    """Active users with a Google social-auth row, an email on file, and no
    usable password. Returns a list of User objects (not a lazy queryset --
    has_usable_password() can't be expressed in SQL, so the final filter
    step is in Python; at prod's current scale (~8.8k Google-auth rows)
    that's a small, one-off cost, not a hot path).

    ``after_id``, when given, restricts to id > after_id -- the restart
    checkpoint described in the module docstring.
    """
    User = get_user_model()
    qs = (
        User.objects
        .filter(social_auth__provider__in=providers, is_active=True)
        .exclude(email='')
        .distinct()
        .order_by('id')
    )
    if after_id is not None:
        qs = qs.filter(id__gt=after_id)
    return [u for u in qs if not u.has_usable_password()]


class Command(BaseCommand):
    help = (
        "Dry-run by default: reports how many active, no-usable-password "
        "Google-auth users (#1237) would receive a 'set a password' email. "
        "Pass --send AND set the %s environment variable to actually send."
        % SEND_ENV_VAR
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--send', action='store_true',
            help="Attempt to actually send. Still a no-op unless the %s "
                 "environment variable is also set to a truthy value "
                 "(1/true/yes)." % SEND_ENV_VAR,
        )
        parser.add_argument(
            '--limit', type=_non_negative_int, default=None,
            help="Only process the first N candidates (ordered by id, "
                 "after --after-id filtering). For rehearsal / "
                 "rate-controlled batches. Must be >= 0.",
        )
        parser.add_argument(
            '--after-id', type=_non_negative_int, default=None, dest='after_id',
            help="Only consider candidates with id greater than this. "
                 "Restart checkpoint: safe against reprocessing anyone "
                 "this command has already ATTEMPTED (success or "
                 "failure) -- NOT a guarantee those ids succeeded. Any "
                 "failed ids from a prior --send run are printed at the "
                 "end and need a separate, deliberate retry; they will "
                 "not be swept up by a later --after-id resume.",
        )
        parser.add_argument(
            '--provider', action='append', dest='providers', default=None,
            choices=list(GOOGLE_PROVIDERS),
            help="Restrict to one provider (repeatable). Default: both "
                 "%s. Useful once Eric confirms which OAuth client Google "
                 "actually flagged." % (GOOGLE_PROVIDERS,),
        )
        parser.add_argument(
            '--verbose-list', action='store_true',
            help="Print every candidate's id/username/email, not just the "
                 "count. Off by default -- this is bulk PII.",
        )
        parser.add_argument(
            '--max-consecutive-failures', type=_non_negative_int,
            default=DEFAULT_MAX_CONSECUTIVE_FAILURES, dest='max_consecutive_failures',
            help="Abort the run if this many attempts in a row fail "
                 "(likely a systemic problem, not isolated bad addresses). "
                 "Default %d; 0 disables the breaker (not recommended for "
                 "a real send)." % DEFAULT_MAX_CONSECUTIVE_FAILURES,
        )

    def handle(self, *args, **options):
        # Re-validated here, not just via argparse's type= on --limit/
        # --after-id/--max-consecutive-failures: call_command(**kwargs)
        # bypasses argparse type conversion for already-typed values
        # (Codex round-2 review, 2026-09-02, reproduced: a programmatic
        # call_command(..., limit=-1) sailed straight through).
        _require_non_negative('--limit', options['limit'])
        _require_non_negative('--after-id', options['after_id'])
        _require_non_negative('--max-consecutive-failures', options['max_consecutive_failures'])

        providers = tuple(options['providers']) if options['providers'] else GOOGLE_PROVIDERS
        candidates = find_candidates(providers=providers, after_id=options['after_id'])
        total_found = len(candidates)

        limit = options['limit']
        if limit is not None:
            candidates = candidates[:limit]

        send_requested = options['send']
        env_opt_in = os.environ.get(SEND_ENV_VAR, '').strip().lower() in ('1', 'true', 'yes')
        will_send = send_requested and env_opt_in

        self.stdout.write(
            "Providers: %s | found %d candidate(s)%s."
            % (
                ', '.join(providers),
                total_found,
                '' if limit is None else (' (processing first %d)' % len(candidates)),
            )
        )

        if send_requested and not env_opt_in:
            self.stdout.write(self.style.WARNING(
                "--send was given but %s is not set to a truthy value in "
                "the environment -- refusing to send anything. This is "
                "deliberate (see command help / module docstring)." % SEND_ENV_VAR
            ))

        if options['verbose_list']:
            for user in candidates:
                self.stdout.write("  id=%s %s <%s>" % (user.pk, user.username, user.email))

        if not will_send:
            self.stdout.write(self.style.NOTICE(
                "DRY RUN -- no email sent. Pass --send and set %s to send "
                "for real." % SEND_ENV_VAR
            ))
            return

        sent, failed_records, skipped = self._send_all(
            candidates, options['max_consecutive_failures'],
        )
        failed = len(failed_records)
        attempted = sent + failed

        summary = "Sent %d, failed %d (attempted %d of %d selected%s)." % (
            sent, failed, attempted, len(candidates),
            '' if not skipped else (', %d never attempted' % skipped),
        )

        if failed_records:
            self.stdout.write(self.style.WARNING(
                "Failed (NOT covered by a later --after-id resume -- "
                "retry these individually): %s"
                % ', '.join('id=%s <%s>' % (pk, email) for pk, email in failed_records)
            ))

        if failed or skipped:
            self.stdout.write(self.style.ERROR(summary))
            raise CommandError(
                "%s Exiting non-zero so a cron/monitoring caller doesn't "
                "read this as clean." % summary
            )
        self.stdout.write(self.style.SUCCESS(summary))

    def _send_all(self, candidates, max_consecutive_failures):
        """Returns (sent_count, failed_records, skipped_count), where
        failed_records is a list of (user_id, email) tuples. skipped_count
        is >0 only if the consecutive-failure circuit breaker tripped
        before reaching every candidate.
        """
        if not candidates:
            # Don't even open a mail connection for an empty batch (Codex
            # round-2 review, 2026-09-02: --send --limit 0 was opening a
            # connection, and failing, for nothing to send).
            return 0, [], 0

        base_url = getattr(settings, 'BASE_URL_SECURE', 'https://unglue.it')
        sent = 0
        failed_records = []
        consecutive_failures = 0
        attempted = 0

        connection = get_connection()
        try:
            # Both of these are deliberately OUTSIDE the per-recipient
            # try/except below: a connection that can't open, or a
            # template that can't render, is a systemic problem and must
            # abort before contacting anyone -- not get treated as one
            # "recipient failure" per candidate (Codex round-1 review).
            connection.open()
            self._render(candidates[0], base_url)

            for user in candidates:
                attempted += 1
                try:
                    self._send_one(user, base_url, connection)
                    sent += 1
                    consecutive_failures = 0
                except Exception as exc:
                    failed_records.append((user.pk, user.email))
                    consecutive_failures += 1
                    self.stderr.write(self.style.ERROR(
                        "Failed to email user id=%s: %s" % (user.pk, exc)
                    ))
                    if max_consecutive_failures and consecutive_failures >= max_consecutive_failures:
                        self.stderr.write(self.style.ERROR(
                            "Aborting: %d consecutive failures (>= "
                            "--max-consecutive-failures=%d) -- this looks "
                            "systemic, not a run of isolated bad addresses."
                            % (consecutive_failures, max_consecutive_failures)
                        ))
                        break
        finally:
            # A close() failure must not swallow the send/fail counts from
            # everything that already succeeded (Codex round-2 review,
            # 2026-09-02: the prior `with get_connection() as connection:`
            # form let an exception from __exit__/close() propagate past
            # the return statement, losing the summary entirely even
            # after real, successful deliveries).
            try:
                connection.close()
            except Exception as close_exc:
                self.stderr.write(self.style.WARNING(
                    "Warning: failed to cleanly close the mail connection "
                    "after sending (%s) -- the send/fail counts above are "
                    "still accurate." % close_exc
                ))

        skipped = len(candidates) - attempted
        return sent, failed_records, skipped

    def _render(self, user, base_url):
        context = {
            'user': user,
            'site_name': 'unglue.it',
            'reset_url': base_url + reverse('libraryauth_password_reset'),
        }
        # autoescape off: this is a plain-text email, not HTML. Without it
        # Django's template engine HTML-escapes context values by default,
        # so a name like "D'Arcy" or "Smith & Sons" would render as
        # "D&#x27;Arcy" / "Smith &amp; Sons" in the actual email body
        # (Codex round-1 review, 2026-09-02, reproduced against the
        # unmodified template).
        subject = render_to_string(SUBJECT_TEMPLATE, context).strip()
        body = render_to_string(BODY_TEMPLATE, context)
        return subject, body

    def _send_one(self, user, base_url, connection):
        subject, body = self._render(user, base_url)
        result = send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
            connection=connection,
        )
        # send_mail() returns the number of messages it believes it
        # delivered. fail_silently=False means most backend failures raise
        # rather than returning 0, but not treating 0 itself as a failure
        # would silently miscount any backend that doesn't raise (Codex
        # round-1 review, 2026-09-02).
        if result != 1:
            raise RuntimeError(
                "send_mail() returned %r (expected 1) for user id=%s" % (result, user.pk)
            )
