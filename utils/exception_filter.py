"""Custom exception-report filter that masks secrets Django's default misses.

Django's SafeExceptionReporterFilter cleanses setting names matching
API|TOKEN|KEY|SECRET|PASS|SIGNATURE. That lets a few real secrets through in
the settings dump emailed on every 500 — notably STRIPE_SK (live Stripe secret)
and EMAIL_HOST_USER (SES SMTP username / AWS access-key id). Broaden the pattern.
See EbookFoundation/security-private#22.
"""
import re

from django.views.debug import SafeExceptionReporterFilter


class RegluitSafeExceptionReporterFilter(SafeExceptionReporterFilter):
    hidden_settings = re.compile(
        "API|TOKEN|KEY|SECRET|PASS|SIGNATURE|STRIPE|EMAIL_HOST_USER|SMTP|CREDENTIAL",
        flags=re.I,
    )
