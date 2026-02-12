# Django Migration Analysis: 1.11 → 5.1

**Date**: 2026-02-12
**Branch**: `django-migration-analysis` (merges PRs #1083, #1084, #1085)
**Tracks**: [#1081](https://github.com/Gluejar/regluit/issues/1081)

## Current State

| Item | Value |
|------|-------|
| Django | 1.11.29 |
| Python | 3.9.11 (.python-version) |
| Database | MySQL (mysqlclient 1.4.6) |
| Server | Python 3.8 on production |
| Target | Django 5.1 + Python 3.12+ |

## Migration Path

```
1.11 → 2.0 → 2.2 LTS → 3.0 → 3.2 LTS → 4.0 → 4.2 LTS → 5.0 → 5.1
```

**Eric's assessment is correct**: 1.11 → 2.0 is the hardest jump. The main obstacles are (1) the `libraryauth` app's deep coupling with old third-party packages and Django internals, and (2) several deprecated API removals that hit at Django 2.0. After 2.2 LTS, the remaining jumps are mostly mechanical find-and-replace (url() → re_path(), ugettext → gettext, etc).

---

## TIER 1: Blocking Issues (Must Fix for Django 2.0)

### 1.1 `libraryauth` — The Central Problem

The `libraryauth` app bundles/imports three legacy packages and adds custom Django internals modifications. This is what Eric meant by "non-standard mods":

#### a) Custom `IPAddressModelField` (libraryauth/models.py:196-227)

```python
class IPAddressModelField(models.GenericIPAddressField):
    def __init__(self, *args, **kwargs):
        models.Field.__init__(self, *args, **kwargs)  # Bypasses GenericIPAddressField.__init__!

    def get_internal_type(self):
        return "PositiveIntegerField"  # Lies about its type to store IPs as integers
```

**Why it's a problem**: This field:
- Extends `GenericIPAddressField` but bypasses its `__init__`
- Reports internal type as `PositiveIntegerField` (for efficient range queries on IP blocks)
- Has a custom `IP` value object (lines 122-168) that wraps int↔IP conversion
- Used by `Block.lower` and `Block.upper` fields for library IP-range authentication
- **Django 2.0+ changed field deconstruct/serialization** — this hack may break migration generation

**Fix**: Either rewrite as a proper custom field with `deconstruct()` method, or replace with two `PositiveIntegerField`s + helper methods. The IP range auth logic is simple enough to not need a custom field type.

#### b) Monkey-patched Registration Validators (libraryauth/forms.py:12-28)

```python
# hack to fix bug in old version of django-registration
from registration.validators import CONFUSABLE_EMAIL
from confusables_homoglyphs import confusables

def validate_confusables_email(value):
    # Custom implementation...

import registration
registration.validators.validate_confusables_email = validate_confusables_email
# end hack
```

**Import-time monkey-patch** of `registration.validators`. Will break if django-registration is updated.

#### c) Library-as-User Pattern (libraryauth/models.py:20-92)

```python
class Library(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, ...)   # Library IS a user
    group = models.OneToOneField(Group, ...)             # Library HAS a group
    owner = models.ForeignKey(AUTH_USER_MODEL, ...)      # Created by this user
```

Plus a `post_save` signal handler that auto-creates Groups with the library's username. This is non-standard but **not blocking** for Django 2.0 — it just needs careful testing.

#### d) Custom Middleware (libraryauth/auth.py:68-87)

```python
class SocialAuthExceptionMiddlewareWithoutMessages(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        # Overrides to skip django.messages
```

Extends `social_django.middleware`. Already uses `MIDDLEWARE` (not `MIDDLEWARE_CLASSES`) in settings. The `process_exception` pattern is still valid in Django 5.1. **Low risk**.

### 1.2 `@transaction.commit_on_success` — ALREADY REMOVED in Django 1.8

**File**: `core/views.py:49`

```python
@transaction.commit_on_success
def test_lock(request):
```

This decorator was **removed in Django 1.6**. The fact it still works means this code path is likely never exercised in production (it's a test view with raw SQL lock testing). **Replace with `@transaction.atomic`** or delete entirely (it looks like a development test artifact).

The raw SQL in this file also uses `%d` string formatting (SQL injection risk):
```python
Campaign.objects.raw("SELECT * FROM core_campaign WHERE id=%d FOR UPDATE" % row_id)
```

### 1.3 `NullBooleanField` — Removed in Django 4.0

| File | Line | Field |
|------|------|-------|
| `core/models/__init__.py` | 111 | `CeleryTask.active = NullBooleanField(default=True)` |
| `payment/models.py` | 93 | `Transaction.approved = NullBooleanField(null=True)` |

**Fix**: `BooleanField(null=True)` + migration.

### 1.4 Direct `User` Model References

**File**: `core/models/__init__.py:1298`
```python
from django.contrib.auth.models import User
# ...
class Gift(models.Model):
    giver = models.ForeignKey(User, ...)  # Should use settings.AUTH_USER_MODEL
```

Most other models correctly use `settings.AUTH_USER_MODEL`. The Gift model and several signal handlers in `core/signals.py` and `core/models/rh_models.py` still import User directly. Not strictly breaking for Django 2.0 (since regluit doesn't define a custom user model), but should fix for correctness.

---

## TIER 2: Required Changes (Django 2.0-4.0 Window)

### 2.1 `url()` → `re_path()` / `path()` — Removed in Django 4.0

**8 URL config files, ~200+ patterns total**:

| File | Approximate `url()` count |
|------|---------------------------|
| `frontend/urls.py` | ~130 |
| `libraryauth/urls.py` | ~30 |
| `api/urls.py` | ~15 |
| `payment/urls.py` | ~12 |
| `urls.py` (root) | ~10 |
| `marc/urls.py` | ~5 |
| `bisac/urls.py` | ~3 |
| `questionnaire/urls.py` | ~3 |

**Fix**: Mechanical replacement. `url(r'...')` → `re_path(r'...')` for all regex patterns. Simple patterns can use `path()`. The `django-upgrade` tool can automate this.

### 2.2 `ugettext_lazy` / `ugettext_noop` → `gettext_lazy` / `gettext_noop` — Removed in Django 4.0

**11 files** use the deprecated `u` prefix versions:

- `core/models/__init__.py`, `core/signals.py`, `core/validation.py`
- `frontend/views/__init__.py`, `frontend/views/rh_views.py`
- `frontend/forms/__init__.py`, `frontend/forms/bibforms.py`, `frontend/forms/rh_forms.py`
- `libraryauth/forms.py`
- `questionnaire/models.py`
- `utils/fields.py`

**Fix**: Find-and-replace. These are aliases that work identically.

### 2.3 `django.utils.http.urlquote` — Removed in Django 3.0

**File**: `libraryauth/auth.py:6`
```python
from django.utils.http import urlquote
```
**Fix**: `from urllib.parse import quote`

### 2.4 Password Reset/Change Views (libraryauth/urls.py)

Old-style function-based auth views (`password_reset`, `password_change`) were replaced with class-based views in Django 2.1. The URL patterns need updating:

```python
# Old:
url(r'^accounts/password/change/$', password_change, {...})
# New:
path('accounts/password/change/', PasswordChangeView.as_view(...))
```

---

## TIER 3: Third-Party Dependency Upgrades

This is where significant effort is needed. Several dependencies are pinned to very old versions.

### Critical Dependencies

| Package | Current | Needed For Django 5.1 | Risk |
|---------|---------|----------------------|------|
| **django-tastypie** | 0.14.1 | 0.14.7+ or **replace with DRF** | HIGH — tastypie is effectively unmaintained |
| **django-storages** | 1.5.2 | 1.14+ | HIGH — S3 backend renamed from `s3boto` to `s3boto3` |
| **social-auth-app-django** | 2.1.0 | 5.x | MEDIUM — API mostly stable, settings may change |
| **django-registration** | 2.4.1 | 3.4+ | MEDIUM — activation workflow changed |
| **django-email-change** | git commit | Find alternative or rewrite | HIGH — unmaintained, pinned to specific commit |
| **django-notification** | git (custom fork) | Fork update or replace | MEDIUM — custom fork, needs Django 2.0+ compat |
| **django-ckeditor** | 5.6.1 | 6.x+ | LOW — mostly backwards compatible |
| **django-extensions** | 3.1.1 | 3.2+ | LOW |
| **django-mptt** | 0.8.6 | 0.14+ | LOW |
| **django-jsonfield** | 1.0.0 | Replace with `django.db.models.JSONField` | MEDIUM — native in Django 3.1+ |

### The Tastypie Question

`django-tastypie` powers the entire API (`api/` app). Options:
1. **Keep tastypie**: The latest release (0.14.7) claims Django 3.2+ support, but it's barely maintained
2. **Replace with Django REST Framework**: More work but much better long-term. DRF is the Django ecosystem standard
3. **Replace with Django Ninja**: Modern, fast, less code — but newer ecosystem

**Recommendation**: Keep tastypie through Django 3.2, then evaluate replacement. The API isn't heavily used and could be simplified.

### The django-email-change Problem

Pinned to a specific git commit from an unmaintained repo:
```
git+git://github.com/novagile/django-email-change.git@0d7cb91b987a...
```

**Recommendation**: Rewrite the email-change functionality inline (it's small — just a confirmation flow). This eliminates an unmaintained dependency.

---

## TIER 4: Architectural Patterns (Not Blocking, But Should Address)

### 4.1 UserProfile OneToOneField Pattern

The codebase uses the older "profile" pattern:
```python
class UserProfile(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, related_name='profile')
```

This is not blocking and still works in Django 5.1, but modern Django recommends `AbstractUser` or `AbstractBaseUser`. **Leave as-is** — changing the user model mid-project with existing data is extremely risky and provides minimal benefit.

### 4.2 Signal Handlers Without `dispatch_uid`

Several `post_save.connect()` calls lack `dispatch_uid`, which can cause duplicate signals in testing. Not blocking but should fix:
- `core/signals.py:59` — `create_user_objects`
- `core/signals.py:63` — `create_api_key`
- `payment/signals.py:33` — `create_user_objects`

### 4.3 Raw SQL in core/views.py

The `test_read`, `test_write`, `test_lock` views use raw SQL with string formatting. These look like development test artifacts (not production code). **Consider deleting entirely**.

---

## Good News (Already Compatible)

These patterns are already correct and don't need changes:

- `MIDDLEWARE` setting (not `MIDDLEWARE_CLASSES`)
- `reverse` / `reverse_lazy` imported from `django.urls`
- Most `ForeignKey` / `OneToOneField` declarations have `on_delete=CASCADE`
- No `django.utils.six` (Python 2 compat layer)
- No `python_2_unicode_compatible` decorator
- No `CommaSeparatedIntegerField`
- No `request.REQUEST`
- No `context_instance` in template rendering
- No `direct_to_template` generic views
- Using `settings.AUTH_USER_MODEL` in most model definitions
- Migrations use proper Django format with `swappable_dependency`

---

## Recommended Migration Strategy

### Approach: Skip-to-LTS with Tooling

Rather than stepping through every minor version, target LTS releases and use automated tooling:

```
Current: Django 1.11.29 / Python 3.9
   ↓
Step 1: Django 2.2 LTS / Python 3.9     (the hard part)
   ↓
Step 2: Django 3.2 LTS / Python 3.10    (medium — mostly url() and ugettext)
   ↓
Step 3: Django 4.2 LTS / Python 3.12    (mechanical — NullBooleanField, etc)
   ↓
Step 4: Django 5.1 / Python 3.12+       (mostly just bumping versions)
```

### Step 1: Django 1.11 → 2.2 LTS (THE HARD PART)

This is ~80% of the total effort. Do it in sub-phases:

**1a. Pre-migration prep (on current Django 1.11)**:
- [ ] Delete `core/views.py` test views (commit_on_success, raw SQL)
- [ ] Fix `Gift.giver` ForeignKey to use `settings.AUTH_USER_MODEL`
- [ ] Fix direct User imports in signal handlers
- [ ] Add `dispatch_uid` to signal handlers
- [ ] Replace `django.utils.http.urlquote` with `urllib.parse.quote`

**1b. Dependency updates (on current Django 1.11, verify still works)**:
- [ ] Update `django-storages` 1.5.2 → latest 1.11.x that supports Django 1.11
- [ ] Update `social-auth-app-django` to latest 2.x
- [ ] Evaluate django-email-change replacement
- [ ] Update `django-registration` to latest that supports 1.11

**1c. Jump to Django 2.2**:
- [ ] `pip install Django==2.2.28`
- [ ] Fix `NullBooleanField` → `BooleanField(null=True)` + migration
- [ ] Fix `IPAddressModelField.deconstruct()` if needed
- [ ] Update password reset views to class-based
- [ ] Run `python manage.py check --deploy`
- [ ] Run test suite
- [ ] Fix any breakage in third-party packages

### Step 2: Django 2.2 → 3.2 LTS

- [ ] `url()` → `re_path()` in all 8 URL files (use `django-upgrade --target-version 3.2`)
- [ ] `ugettext_lazy` → `gettext_lazy` (11 files)
- [ ] `urlquote` → `urllib.parse.quote`
- [ ] Replace `django-jsonfield` with native `JSONField`
- [ ] Update Python to 3.10+
- [ ] Update all third-party packages to Django 3.2-compatible versions

### Step 3: Django 3.2 → 4.2 LTS

- [ ] Run `django-upgrade --target-version 4.2` for automated fixes
- [ ] Evaluate tastypie replacement
- [ ] Update all remaining third-party packages

### Step 4: Django 4.2 → 5.1

- [ ] Should be mostly painless at this point
- [ ] Update Python to 3.12+
- [ ] Final third-party package updates

---

## Tooling Recommendations

1. **[django-upgrade](https://github.com/adamchainz/django-upgrade)** — Automated code fixer for deprecated patterns. Can handle url(), ugettext, NullBooleanField, etc.
2. **[pyupgrade](https://github.com/asottile/pyupgrade)** — Python syntax modernization
3. **Django's `check` framework**: `python manage.py check --deploy` at each step
4. **Deprecation warnings**: Run tests with `-Wd` to see all Django deprecation warnings

---

## Effort Estimate by Component

| Component | Files | Effort | Notes |
|-----------|-------|--------|-------|
| `libraryauth` (IPAddressModelField, monkey-patches) | 5 | **HIGH** | Custom field is the riskiest change |
| URL patterns (url → re_path) | 8 | Medium | Mechanical, use django-upgrade |
| Translation imports (ugettext → gettext) | 11 | Low | Find-and-replace |
| Third-party dependency updates | ~15 packages | **HIGH** | Testing-intensive |
| NullBooleanField replacement | 2+migrations | Low | Straightforward |
| core/views.py cleanup | 1 | Low | Delete test artifacts |
| Password reset views | 1 | Low | Class-based replacement |
| django-email-change replacement | ~3 | Medium | Small rewrite |
| Tastypie evaluation | api/ app | Medium-High | If replacing with DRF |

**Total estimated effort**: The 1.11 → 2.2 jump is likely 2-3 weeks of focused work. Each subsequent LTS jump is 3-5 days. Total: ~1 month with testing.

---

## Files Inventory (Needs Changes)

### Must change for Django 2.0:
- `core/views.py` — delete test views or fix transaction decorator
- `core/models/__init__.py` — NullBooleanField, Gift User FK
- `payment/models.py` — NullBooleanField
- `libraryauth/models.py` — IPAddressModelField review
- `libraryauth/forms.py` — monkey-patch review
- `libraryauth/auth.py` — urlquote
- `libraryauth/urls.py` — password views

### Must change for Django 4.0:
- All 8 `urls.py` files — url() → re_path()
- 11 files — ugettext → gettext

### Dependencies to update:
- `requirements.txt` / `requirements_versioned.pip` — version bumps
- `Pipfile` — if using pipenv
- `settings/common.py` — INSTALLED_APPS, MIDDLEWARE if needed
- `settings/prod.py` — django-storages S3 backend
