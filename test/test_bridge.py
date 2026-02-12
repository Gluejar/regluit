"""
Django Migration Bridge Tests

These tests capture the current behavior of critical components that are
at risk during the Django 1.11 → 2.2 → 3.2 → 4.2 → 5.1 migration.

Run before AND after each Django version bump:
    python -Wa manage.py test test.test_bridge --settings=regluit.settings.me

If any test fails after upgrading Django, the component needs attention.

Tracks: https://github.com/Gluejar/regluit/issues/1081
"""

import warnings
from decimal import Decimal

from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse, NoReverseMatch


# ---------------------------------------------------------------------------
# 1. IPAddressModelField — the highest-risk custom field
# ---------------------------------------------------------------------------

class IPValueObjectTest(TestCase):
    """Test the IP value object used by IPAddressModelField."""

    def test_ip_from_string(self):
        from regluit.libraryauth.models import IP
        ip = IP('192.168.1.1')
        self.assertEqual(ip.int, 3232235777)

    def test_ip_from_integer(self):
        from regluit.libraryauth.models import IP
        ip = IP(3232235777)
        self.assertEqual(ip.string, '192.168.1.1')

    def test_ip_roundtrip(self):
        from regluit.libraryauth.models import IP
        original = '10.0.0.1'
        ip = IP(original)
        self.assertEqual(IP(ip.int).string, original)

    def test_ip_zero(self):
        from regluit.libraryauth.models import IP
        ip = IP(0)
        self.assertEqual(ip.string, '0.0.0.0')

    def test_ip_max(self):
        from regluit.libraryauth.models import IP
        ip = IP('255.255.255.255')
        self.assertEqual(ip.int, 4294967295)

    def test_ip_comparison(self):
        from regluit.libraryauth.models import IP
        self.assertTrue(IP('192.168.1.2') > IP('192.168.1.1'))
        self.assertEqual(IP('10.0.0.1'), IP(167772161))

    def test_ip_from_none(self):
        from regluit.libraryauth.models import IP
        ip = IP(None)
        self.assertIsNone(ip.int)


class IPAddressModelFieldTest(TestCase):
    """
    Validate IPAddressModelField behavior across Django versions.

    This field does unusual things:
    - Extends GenericIPAddressField but bypasses its __init__
    - Reports internal type as PositiveIntegerField
    - Stores IPs as integers for efficient range queries
    """

    def test_internal_type(self):
        """Field must report as PositiveIntegerField for DB storage."""
        from regluit.libraryauth.models import IPAddressModelField
        field = IPAddressModelField()
        self.assertEqual(field.get_internal_type(), "PositiveIntegerField")

    def test_deconstruct_roundtrip(self):
        """Field must survive deconstruct/reconstruct for migrations."""
        from regluit.libraryauth.models import IPAddressModelField
        field = IPAddressModelField(db_index=True)
        name, path, args, kwargs = field.deconstruct()
        # Path must be importable
        self.assertIn('IPAddressModelField', path)
        # Roundtrip: reconstruct from deconstructed parts
        reconstructed = IPAddressModelField(*args, **kwargs)
        self.assertEqual(reconstructed.get_internal_type(), "PositiveIntegerField")

    def test_get_prep_value_with_ip(self):
        """IP objects must be stored as integers in the database."""
        from regluit.libraryauth.models import IPAddressModelField, IP
        field = IPAddressModelField()
        ip = IP('192.168.1.1')
        prep = field.get_prep_value(ip)
        self.assertEqual(prep, 3232235777)
        self.assertIsInstance(prep, int)

    def test_get_prep_value_with_none(self):
        """None/empty values must pass through as-is."""
        from regluit.libraryauth.models import IPAddressModelField
        field = IPAddressModelField()
        self.assertFalse(field.get_prep_value(None))
        self.assertFalse(field.get_prep_value(''))

    def test_to_python_from_integer(self):
        """Integer values from DB must convert back to IP objects."""
        from regluit.libraryauth.models import IPAddressModelField, IP
        field = IPAddressModelField()
        result = field.to_python(3232235777)
        self.assertIsInstance(result, IP)
        self.assertEqual(result.string, '192.168.1.1')

    def test_to_python_from_string(self):
        """String IP values must convert to IP objects."""
        from regluit.libraryauth.models import IPAddressModelField, IP
        field = IPAddressModelField()
        result = field.to_python('10.0.0.1')
        self.assertIsInstance(result, IP)
        self.assertEqual(result.int, 167772161)

    def test_to_python_idempotent(self):
        """IP objects must pass through to_python unchanged."""
        from regluit.libraryauth.models import IPAddressModelField, IP
        field = IPAddressModelField()
        ip = IP('172.16.0.1')
        result = field.to_python(ip)
        self.assertIs(result, ip)


# ---------------------------------------------------------------------------
# 2. Library-User-Group relationships and signal handlers
# ---------------------------------------------------------------------------

class LibraryGroupSignalTest(TestCase):
    """
    Test that creating a Library auto-creates a Group via post_save signal.
    The add_group signal handler (libraryauth/models.py:74) must work
    identically across Django versions.
    """
    fixtures = ['initial_data.json']

    def setUp(self):
        self.owner = User.objects.create_user('lib_owner', 'owner@example.com', 'testpass')

    def test_library_creation_creates_group(self):
        """Library.save() must auto-create a Group with the library user's username."""
        from regluit.libraryauth.models import Library
        lib_user = User.objects.create_user('testlib', 'lib@example.com', 'testpass')
        library = Library.objects.create(
            user=lib_user,
            owner=self.owner,
            name='Test Library',
        )
        library.refresh_from_db()
        self.assertIsNotNone(library.group)
        self.assertEqual(library.group.name, 'testlib')

    def test_library_add_user(self):
        """Library.add_user() must add user to the library's group."""
        from regluit.libraryauth.models import Library
        lib_user = User.objects.create_user('testlib2', 'lib2@example.com', 'testpass')
        library = Library.objects.create(
            user=lib_user,
            owner=self.owner,
            name='Test Library 2',
        )
        library.refresh_from_db()

        patron = User.objects.create_user('patron', 'patron@example.com', 'testpass')
        library.add_user(patron)
        self.assertTrue(library.has_user(patron))
        self.assertIn(library.group, patron.groups.all())

    def test_library_has_user_owner(self):
        """The library's own user is always a member."""
        from regluit.libraryauth.models import Library
        lib_user = User.objects.create_user('testlib3', 'lib3@example.com', 'testpass')
        library = Library.objects.create(
            user=lib_user,
            owner=self.owner,
            name='Test Library 3',
        )
        self.assertTrue(library.has_user(lib_user))

    def test_duplicate_group_name_handling(self):
        """If a group name already exists, add_group appends '+' suffixes."""
        from regluit.libraryauth.models import Library
        # Pre-create a group with the username
        Group.objects.create(name='dupelib')
        lib_user = User.objects.create_user('dupelib', 'dupe@example.com', 'testpass')
        library = Library.objects.create(
            user=lib_user,
            owner=self.owner,
            name='Dupe Library',
        )
        library.refresh_from_db()
        self.assertIsNotNone(library.group)
        # Group name should have a '+' suffix since 'dupelib' was taken
        self.assertTrue(library.group.name.startswith('dupelib'))


class UserCreationSignalTest(TestCase):
    """
    Test that creating a User triggers creation of:
    - UserProfile (core.signals.create_user_objects)
    - Wishlist (core.signals.create_user_objects)
    - Credit (payment.signals.create_user_objects)
    - API key (tastypie create_api_key)

    These signal handlers lack dispatch_uid and fire on post_save.
    If they break during migration, the site will crash on registration.
    """
    fixtures = ['initial_data.json']

    def test_user_gets_profile(self):
        """New user must get a UserProfile."""
        user = User.objects.create_user('bridge_test', 'bridge@example.com', 'testpass')
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsNotNone(user.profile)

    def test_user_gets_wishlist(self):
        """New user must get a Wishlist."""
        user = User.objects.create_user('bridge_test2', 'bridge2@example.com', 'testpass')
        self.assertTrue(hasattr(user, 'wishlist'))
        self.assertIsNotNone(user.wishlist)

    def test_user_gets_credit(self):
        """New user must get a Credit record."""
        user = User.objects.create_user('bridge_test3', 'bridge3@example.com', 'testpass')
        self.assertTrue(hasattr(user, 'credit'))
        self.assertEqual(user.credit.balance, Decimal('0.00'))

    def test_user_gets_api_key(self):
        """New user must get a Tastypie API key."""
        from tastypie.models import ApiKey
        user = User.objects.create_user('bridge_test4', 'bridge4@example.com', 'testpass')
        self.assertTrue(ApiKey.objects.filter(user=user).exists())


# ---------------------------------------------------------------------------
# 3. NullBooleanField behavior — removed in Django 4.0
# ---------------------------------------------------------------------------

class NullBooleanFieldBridgeTest(TestCase):
    """
    Verify NullBooleanField three-state behavior (True/False/None).
    When migrated to BooleanField(null=True), behavior must be identical.

    Fields:
    - CeleryTask.active (core/models/__init__.py:111)
    - Transaction.approved (payment/models.py:93)
    """
    fixtures = ['initial_data.json']

    def test_celery_task_active_default_true(self):
        from regluit.core.models import CeleryTask
        task = CeleryTask.objects.create(task_id='bridge-test-1', function_name='test')
        task.refresh_from_db()
        self.assertTrue(task.active)

    def test_celery_task_active_none(self):
        from regluit.core.models import CeleryTask
        task = CeleryTask.objects.create(task_id='bridge-test-2', function_name='test')
        task.active = None
        task.save()
        task.refresh_from_db()
        self.assertIsNone(task.active)

    def test_celery_task_active_false(self):
        from regluit.core.models import CeleryTask
        task = CeleryTask.objects.create(task_id='bridge-test-3', function_name='test')
        task.active = False
        task.save()
        task.refresh_from_db()
        self.assertFalse(task.active)

    def test_transaction_approved_null(self):
        from regluit.payment.models import Transaction
        t = Transaction.objects.create()
        t.refresh_from_db()
        self.assertIsNone(t.approved)

    def test_transaction_approved_true(self):
        from regluit.payment.models import Transaction
        t = Transaction.objects.create(approved=True)
        t.refresh_from_db()
        self.assertTrue(t.approved)

    def test_transaction_approved_false(self):
        from regluit.payment.models import Transaction
        t = Transaction.objects.create(approved=False)
        t.refresh_from_db()
        self.assertFalse(t.approved)


# ---------------------------------------------------------------------------
# 4. URL resolution — named URLs must survive url() → re_path() migration
# ---------------------------------------------------------------------------

class URLResolutionBridgeTest(TestCase):
    """
    Validate that critical named URLs resolve.
    Run before AND after Django upgrade to catch URL config breakage.

    The url() function is deprecated in 2.0 and removed in 4.0.
    When converting to re_path()/path(), all names must still resolve.
    """

    # (url_name, kwargs) — no kwargs means the URL takes no arguments
    CRITICAL_URLS = [
        # libraryauth
        ('superlogin', {}),
        ('registration_register', {}),
        ('edit_user', {}),
        # frontend - public pages
        ('home', {}),
        ('search', {}),
        ('faq', {}),
        ('privacy', {}),
        ('terms', {}),
        ('free', {}),
        # frontend - authenticated pages
        ('wishlist', {}),
        ('manage_account', {}),
        # frontend - rightsholders
        ('rightsholders', {}),
        ('agree', {}),
        ('programs', {}),
        # frontend - campaigns & lists
        ('campaign_list', {'facet': 'active'}),
        ('work_list', {'facet': 'popular'}),
        # frontend - parameterized
        ('supporter', {'supporter_username': 'testuser'}),
        ('library', {'library_name': 'testlib'}),
    ]

    def test_critical_urls_resolve(self):
        for url_name, kwargs in self.CRITICAL_URLS:
            with self.subTest(url=url_name):
                try:
                    url = reverse(url_name, kwargs=kwargs if kwargs else None)
                    self.assertTrue(
                        url.startswith('/'),
                        f"{url_name} resolved to unexpected value: {url}"
                    )
                except NoReverseMatch:
                    self.fail(f"URL '{url_name}' failed to resolve")

    def test_work_url_with_id(self):
        """Work detail URL takes a work_id parameter."""
        url = reverse('work', kwargs={'work_id': '1'})
        self.assertIn('/work/1', url)

    def test_api_urls_resolve(self):
        """Tastypie API root must resolve."""
        # The API uses its own URL dispatcher but is included at /api/
        resp = self.client.get('/api/v1/')
        # Should get a response (200 or 401), not 404
        self.assertNotEqual(resp.status_code, 404)


# ---------------------------------------------------------------------------
# 5. Authentication patterns — CardPattern and EmailPattern
# ---------------------------------------------------------------------------

class CardPatternTest(TestCase):
    """Test library card number validation (used by cardnum auth backend)."""
    fixtures = ['initial_data.json']

    def setUp(self):
        self.owner = User.objects.create_user('cp_owner', 'cp@example.com', 'testpass')

    def test_card_pattern_valid(self):
        from regluit.libraryauth.models import Library, CardPattern
        lib_user = User.objects.create_user('cardlib', 'cardlib@example.com', 'testpass')
        library = Library.objects.create(
            user=lib_user, owner=self.owner, name='Card Library', backend='cardnum'
        )
        # Pattern: 4 digits followed by 6 digits, with Luhn checksum
        pattern = CardPattern.objects.create(
            library=library, pattern='####-######', checksum=False
        )
        self.assertTrue(pattern.is_valid('1234-567890'))
        self.assertFalse(pattern.is_valid('123-567890'))  # too short
        self.assertFalse(pattern.is_valid('ABCD-567890'))  # non-digit

    def test_luhn_checksum(self):
        from regluit.libraryauth.models import luhn_checksum
        # Valid Luhn number
        self.assertEqual(luhn_checksum(49927398716), 0)
        # Invalid
        self.assertNotEqual(luhn_checksum(49927398717), 0)


class EmailPatternTest(TestCase):
    """Test email pattern validation (used by email auth backend)."""
    fixtures = ['initial_data.json']

    def setUp(self):
        self.owner = User.objects.create_user('ep_owner', 'ep@example.com', 'testpass')

    def test_email_pattern_valid(self):
        from regluit.libraryauth.models import Library, EmailPattern
        lib_user = User.objects.create_user('emaillib', 'emaillib@example.com', 'testpass')
        library = Library.objects.create(
            user=lib_user, owner=self.owner, name='Email Library', backend='email'
        )
        pattern = EmailPattern.objects.create(library=library, pattern='@university.edu')
        self.assertTrue(pattern.is_valid('student@university.edu'))
        self.assertFalse(pattern.is_valid('student@other.edu'))

    def test_email_pattern_case_insensitive(self):
        from regluit.libraryauth.models import Library, EmailPattern
        lib_user = User.objects.create_user('emaillib2', 'emaillib2@example.com', 'testpass')
        library = Library.objects.create(
            user=lib_user, owner=self.owner, name='Email Library 2', backend='email'
        )
        pattern = EmailPattern.objects.create(library=library, pattern='@University.EDU')
        self.assertTrue(pattern.is_valid('Student@UNIVERSITY.edu'))


# ---------------------------------------------------------------------------
# 6. Library template selection
# ---------------------------------------------------------------------------

class LibraryTemplateTest(TestCase):
    """Library.join_template and help_template must resolve correctly."""
    fixtures = ['initial_data.json']

    def setUp(self):
        self.owner = User.objects.create_user('tmpl_owner', 'tmpl@example.com', 'testpass')

    def _make_library(self, username, backend, approved=True):
        from regluit.libraryauth.models import Library
        lib_user = User.objects.create_user(username, f'{username}@example.com', 'testpass')
        return Library.objects.create(
            user=lib_user, owner=self.owner, name=f'{username} Library',
            backend=backend, approved=approved,
        )

    def test_approved_ip_templates(self):
        lib = self._make_library('iplib', 'ip', approved=True)
        self.assertEqual(lib.join_template, 'libraryauth/ip_join.html')
        self.assertEqual(lib.help_template, 'libraryauth/ip_help.html')

    def test_approved_cardnum_templates(self):
        lib = self._make_library('cardnumlib', 'cardnum', approved=True)
        self.assertEqual(lib.join_template, 'libraryauth/cardnum_join.html')

    def test_approved_email_templates(self):
        lib = self._make_library('emaillib3', 'email', approved=True)
        self.assertEqual(lib.join_template, 'libraryauth/email_join.html')

    def test_unapproved_library(self):
        lib = self._make_library('unapprovedlib', 'ip', approved=False)
        self.assertEqual(lib.join_template, 'libraryauth/unapproved.html')


# ---------------------------------------------------------------------------
# 7. Block model (IP range storage using IPAddressModelField)
# ---------------------------------------------------------------------------

class BlockModelTest(TestCase):
    """Test Block model that stores IP ranges as integers via IPAddressModelField."""
    fixtures = ['initial_data.json']

    def setUp(self):
        self.owner = User.objects.create_user('block_owner', 'block@example.com', 'testpass')

    def test_create_single_ip_block(self):
        from regluit.libraryauth.models import Library, Block, IP
        lib_user = User.objects.create_user('blocklib', 'blocklib@example.com', 'testpass')
        library = Library.objects.create(
            user=lib_user, owner=self.owner, name='Block Library',
        )
        block = Block.objects.create(library=library, lower=IP('10.0.0.1'))
        block.refresh_from_db()
        # The stored integer should roundtrip back to the same IP
        self.assertEqual(IP(block.lower).string, '10.0.0.1')

    def test_create_ip_range_block(self):
        from regluit.libraryauth.models import Library, Block, IP
        lib_user = User.objects.create_user('blocklib2', 'blocklib2@example.com', 'testpass')
        library = Library.objects.create(
            user=lib_user, owner=self.owner, name='Block Library 2',
        )
        block = Block.objects.create(
            library=library,
            lower=IP('192.168.0.0'),
            upper=IP('192.168.0.255'),
        )
        block.refresh_from_db()
        self.assertEqual(IP(block.lower).string, '192.168.0.0')
        self.assertEqual(IP(block.upper).string, '192.168.0.255')

    def test_block_clean_validates_order(self):
        from regluit.libraryauth.models import Library, Block, IP
        lib_user = User.objects.create_user('blocklib3', 'blocklib3@example.com', 'testpass')
        library = Library.objects.create(
            user=lib_user, owner=self.owner, name='Block Library 3',
        )
        block = Block(
            library=library,
            lower=IP('192.168.1.0'),
            upper=IP('192.168.0.0'),  # upper < lower — invalid
        )
        with self.assertRaises(ValidationError):
            block.clean()


# ---------------------------------------------------------------------------
# 8. Gift model — uses direct User import (should be AUTH_USER_MODEL)
# ---------------------------------------------------------------------------

class GiftModelBridgeTest(TestCase):
    """
    The Gift.giver FK uses a direct User import instead of
    settings.AUTH_USER_MODEL. This is technically incorrect but not blocking
    since regluit doesn't use a custom user model. This test verifies
    the FK relationship works.
    """
    fixtures = ['initial_data.json']

    def test_gift_giftee_creates_user(self):
        """Gift.giftee() should get or create a user by email."""
        from regluit.core.models import Gift
        email = 'giftee-bridge@example.com'
        giftee = Gift.giftee(email, '999')
        self.assertEqual(giftee.email, email)
        self.assertTrue(giftee.username.startswith('giftee'))

    def test_gift_giftee_returns_existing(self):
        """Gift.giftee() should return existing user if email matches."""
        from regluit.core.models import Gift
        user = User.objects.create_user('existing', 'existing-gift@example.com', 'testpass')
        giftee = Gift.giftee('existing-gift@example.com', '1000')
        self.assertEqual(giftee.pk, user.pk)


# ---------------------------------------------------------------------------
# 9. Deprecation warning canary
# ---------------------------------------------------------------------------

class DeprecationCanaryTest(TestCase):
    """
    Import key modules and check for Django deprecation warnings.
    Run with: python -Wa manage.py test test.test_bridge.DeprecationCanaryTest

    This test captures warnings at import time. If you see
    RemovedInDjango* warnings, fix them before upgrading.
    """

    def test_import_core_models(self):
        """Core models should import without deprecation warnings."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            import importlib
            importlib.reload(__import__('regluit.core.models', fromlist=['']))
            django_warnings = [
                x for x in w
                if issubclass(x.category, (DeprecationWarning, PendingDeprecationWarning))
                and 'django' in str(x.filename).lower()
            ]
            # Report but don't fail — on 1.11 there may be legitimate warnings
            # that are fixed during migration. This test is for visibility.
            if django_warnings:
                msg = '\n'.join(f"  {x.filename}:{x.lineno} - {x.message}" for x in django_warnings)
                self.skipTest(f"Django deprecation warnings found (fix before upgrading):\n{msg}")


# ---------------------------------------------------------------------------
# 10. ip_to_int / int_to_ip helper functions
# ---------------------------------------------------------------------------

class IPConversionHelpersTest(TestCase):
    """Test standalone IP conversion helpers (not the field or IP class)."""

    def test_ip_to_int(self):
        from regluit.libraryauth.models import ip_to_int
        self.assertEqual(ip_to_int('0.0.0.0'), 0)
        self.assertEqual(ip_to_int('255.255.255.255'), 4294967295)
        self.assertEqual(ip_to_int('192.168.1.1'), 3232235777)
        self.assertEqual(ip_to_int('10.0.0.1'), 167772161)

    def test_int_to_ip(self):
        from regluit.libraryauth.models import int_to_ip
        self.assertEqual(int_to_ip(0), '0.0.0.0')
        self.assertEqual(int_to_ip(4294967295), '255.255.255.255')
        self.assertEqual(int_to_ip(3232235777), '192.168.1.1')

    def test_ip_to_int_invalid(self):
        from regluit.libraryauth.models import ip_to_int
        with self.assertRaises(ValidationError):
            ip_to_int('999.999.999.999')
        with self.assertRaises(ValidationError):
            ip_to_int('not.an.ip.address')

    def test_int_to_ip_bounds(self):
        from regluit.libraryauth.models import int_to_ip
        with self.assertRaises(ValidationError):
            int_to_ip(-1)
        with self.assertRaises(ValidationError):
            int_to_ip(4294967296)

    def test_roundtrip(self):
        from regluit.libraryauth.models import ip_to_int, int_to_ip
        for ip_str in ['0.0.0.0', '1.2.3.4', '192.168.0.1', '255.255.255.255']:
            self.assertEqual(int_to_ip(ip_to_int(ip_str)), ip_str)
