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

Not built here, deliberately out of scope for this pass (see REPORT):
persistent "already emailed" tracking across runs (so a second run doesn't
re-email the same person) and batching/rate-limiting for a real send.
``--limit`` covers rehearsal-scale runs; a real send needs one or both of
those first.
"""
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
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


def find_candidates(providers=GOOGLE_PROVIDERS):
    """Active users with a Google social-auth row, an email on file, and no
    usable password. Returns a list of User objects (not a lazy queryset --
    has_usable_password() can't be expressed in SQL, so the final filter
    step is in Python; at prod's current scale (~8.8k Google-auth rows)
    that's a small, one-off cost, not a hot path).
    """
    User = get_user_model()
    qs = (
        User.objects
        .filter(social_auth__provider__in=providers, is_active=True)
        .exclude(email='')
        .distinct()
        .order_by('id')
    )
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
            '--limit', type=int, default=None,
            help="Only process the first N candidates (ordered by id). "
                 "For rehearsal / rate-controlled batches.",
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
            help="Print every candidate's username/email, not just the "
                 "count. Off by default -- this is bulk PII.",
        )

    def handle(self, *args, **options):
        providers = tuple(options['providers']) if options['providers'] else GOOGLE_PROVIDERS
        candidates = find_candidates(providers=providers)
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
                self.stdout.write("  %s <%s>" % (user.username, user.email))

        if not will_send:
            self.stdout.write(self.style.NOTICE(
                "DRY RUN -- no email sent. Pass --send and set %s to send "
                "for real." % SEND_ENV_VAR
            ))
            return

        sent, failed = 0, 0
        for user in candidates:
            try:
                self._send_one(user)
                sent += 1
            except Exception as exc:  # pragma: no cover - defensive; surfaced below
                failed += 1
                self.stderr.write(self.style.ERROR(
                    "Failed to email user id=%s: %s" % (user.pk, exc)
                ))
        self.stdout.write(self.style.SUCCESS("Sent %d, failed %d." % (sent, failed)))

    def _send_one(self, user):
        base_url = getattr(settings, 'BASE_URL_SECURE', 'https://unglue.it')
        context = {
            'user': user,
            'site_name': 'unglue.it',
            'reset_url': base_url + reverse('libraryauth_password_reset'),
        }
        subject = render_to_string(SUBJECT_TEMPLATE, context).strip()
        body = render_to_string(BODY_TEMPLATE, context)
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
