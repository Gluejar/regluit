import os
from unittest import mock
from unittest.mock import MagicMock

from django.core.mail import EmailMessage
from django.test import TestCase, override_settings

from regluit.utils.safe_email_backend import (
    ALLOWLIST_BACKEND_PATH,
    AllowlistEmailBackend,
    _is_allowed,
    resolve_email_backend,
)


class TestIsAllowed(TestCase):
    def test_allowed_domain(self):
        self.assertTrue(_is_allowed('someone@ebookfoundation.org', {'ebookfoundation.org'}, set()))

    def test_allowed_address(self):
        self.assertTrue(_is_allowed('raymond.yee@gmail.com', set(), {'raymond.yee@gmail.com'}))

    def test_not_allowed(self):
        self.assertFalse(_is_allowed('realuser@example.com', {'ebookfoundation.org'}, set()))

    def test_case_insensitive(self):
        self.assertTrue(_is_allowed('Someone@EbookFoundation.ORG', {'ebookfoundation.org'}, set()))

    def test_empty_address_is_harmless(self):
        # Nothing to protect against an unused To/Cc/Bcc slot.
        self.assertTrue(_is_allowed('', {'ebookfoundation.org'}, set()))

    def test_domain_confusion_not_allowed(self):
        # 'notebookfoundation.org' must not match an allowlisted
        # 'ebookfoundation.org' via a loose substring check.
        self.assertFalse(_is_allowed('x@notebookfoundation.org', {'ebookfoundation.org'}, set()))


@override_settings(
    EMAIL_SAFE_MODE_ALLOWED_DOMAINS='ebookfoundation.org,gluejar.com',
    EMAIL_SAFE_MODE_ALLOWED_ADDRESSES='raymond.yee@gmail.com',
    EMAIL_SAFE_MODE_REDIRECT_TO='staging-catchall@ebookfoundation.org',
)
class TestAllowlistEmailBackend(TestCase):
    """Regression guard for regluit#1238: a staging box whose DB is a copy
    of production must never deliver real email to real users. Constructing
    AllowlistEmailBackend() is safe in a test even with the real SMTP
    backend as its default wrapped class -- Django's SMTP backend doesn't
    open a socket until send_messages()/open() is actually called, and
    every test here swaps in a MagicMock before calling send_messages().
    """

    def _backend_with_fake_real(self):
        backend = AllowlistEmailBackend()
        backend.real_backend = MagicMock()
        backend.real_backend.send_messages.return_value = 1
        return backend

    def test_fully_allowlisted_message_passes_through_unchanged(self):
        backend = self._backend_with_fake_real()
        msg = EmailMessage(subject='Hi', body='body', to=['someone@ebookfoundation.org'])
        backend.send_messages([msg])
        sent = backend.real_backend.send_messages.call_args[0][0]
        self.assertEqual(1, len(sent))
        self.assertIs(sent[0], msg)
        self.assertEqual(['someone@ebookfoundation.org'], sent[0].to)

    def test_non_allowlisted_message_is_redirected(self):
        backend = self._backend_with_fake_real()
        msg = EmailMessage(subject='Password reset', body='click here', to=['realuser@example.com'])
        backend.send_messages([msg])
        sent = backend.real_backend.send_messages.call_args[0][0]
        self.assertEqual(['staging-catchall@ebookfoundation.org'], sent[0].to)
        self.assertIn('realuser@example.com', sent[0].subject)
        self.assertIn('realuser@example.com', sent[0].body)
        # The original message object passed in by calling code is never
        # mutated -- only the copy handed to the real backend is changed.
        self.assertEqual(['realuser@example.com'], msg.to)

    def test_mixed_allowlisted_and_real_recipients_still_redirects(self):
        backend = self._backend_with_fake_real()
        msg = EmailMessage(
            subject='Notice', body='body',
            to=['someone@ebookfoundation.org', 'realuser@example.com'],
        )
        backend.send_messages([msg])
        sent = backend.real_backend.send_messages.call_args[0][0]
        self.assertEqual(['staging-catchall@ebookfoundation.org'], sent[0].to)

    def test_cc_and_bcc_are_checked_too(self):
        backend = self._backend_with_fake_real()
        msg = EmailMessage(
            subject='Notice', body='body', to=['someone@ebookfoundation.org'],
            cc=['realuser@example.com'],
        )
        backend.send_messages([msg])
        sent = backend.real_backend.send_messages.call_args[0][0]
        self.assertEqual(['staging-catchall@ebookfoundation.org'], sent[0].to)
        self.assertEqual([], sent[0].cc)

    @override_settings(EMAIL_SAFE_MODE_REDIRECT_TO='')
    def test_refuses_to_send_without_a_redirect_target(self):
        # No silent drop, no silent send to an unknown address -- fail
        # loudly so the gap gets noticed and configured, not shipped quiet.
        backend = self._backend_with_fake_real()
        msg = EmailMessage(subject='x', body='y', to=['realuser@example.com'])
        with self.assertRaises(RuntimeError):
            backend.send_messages([msg])
        backend.real_backend.send_messages.assert_not_called()

    def test_empty_message_list_is_a_noop(self):
        backend = self._backend_with_fake_real()
        result = backend.send_messages([])
        self.assertEqual(0, result)
        backend.real_backend.send_messages.assert_not_called()


class TestResolveEmailBackend(TestCase):
    """Regression guard for settings/common.py's EMAIL_SAFE_MODE wiring.

    This is deliberately NOT a test that imports django.conf.settings and
    checks EMAIL_BACKEND from inside a TestCase -- Django's test runner
    (setup_test_environment) unconditionally overwrites
    settings.EMAIL_BACKEND with the locmem backend before any test body
    runs, so a check like that would pass even if settings/common.py's
    conditional were broken (accidentally unconditional, inverted, etc.) --
    caught in CC review, 2026-08-31. Testing resolve_email_backend()
    directly, with no settings module involved, is what actually exercises
    the decision logic settings/common.py delegates to.
    """

    def test_off_leaves_backend_unchanged(self):
        real, effective = resolve_email_backend(False, 'some.RealBackend', env={})
        self.assertEqual('some.RealBackend', real)
        self.assertEqual('some.RealBackend', effective)

    def test_on_wraps_the_current_backend_by_default(self):
        real, effective = resolve_email_backend(True, 'some.RealBackend', env={})
        self.assertEqual('some.RealBackend', real)
        self.assertEqual(ALLOWLIST_BACKEND_PATH, effective)

    def test_on_honors_an_explicit_real_backend_override(self):
        real, effective = resolve_email_backend(
            True, 'some.RealBackend',
            env={'SAFE_EMAIL_REAL_BACKEND': 'django.core.mail.backends.console.EmailBackend'},
        )
        self.assertEqual('django.core.mail.backends.console.EmailBackend', real)
        self.assertEqual(ALLOWLIST_BACKEND_PATH, effective)

    def test_defaults_to_os_environ_when_no_env_passed(self):
        # settings/common.py calls this with no `env` argument in
        # production -- confirm that path reads the real process
        # environment rather than silently doing nothing.
        with mock.patch.dict(os.environ, {'SAFE_EMAIL_REAL_BACKEND': 'x.RealBackend'}):
            real, effective = resolve_email_backend(True, 'some.RealBackend')
        self.assertEqual('x.RealBackend', real)
        self.assertEqual(ALLOWLIST_BACKEND_PATH, effective)
