# IP address part of this of this copied from
# https://github.com/benliles/django-ipauth/blob/master/ipauth/models.py

import re
from django.contrib.auth.models import Group
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core import validators
from django.db import models
from django.db.models.signals import post_save
from django.forms import GenericIPAddressField as BaseIPAddressField
from django.urls import reverse

class Library(models.Model):
    '''
    name and other things derive from the User
    '''
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='library',
    )
    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name='library',
        null=True
        )
    backend = models.CharField(max_length=10, choices=(
        ('ip', 'IP authentication'),
        ('cardnum', 'Library Card Number check'),
        ('email', 'e-mail pattern check'),
    ), default='ip')
    name = models.CharField(max_length=80, default='')
    approved = models.BooleanField(default=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="libraries",
    )
    credential = None

    def __unicode__(self):
        return unicode(self.name)

    def add_user(self, user):
        user.groups.add(self.group)
        (library_user, created) = LibraryUser.objects.get_or_create(library=self, user=user)
        library_user.credential = self.credential
        library_user.save()

    def has_user(self, user):
        return self.group in user.groups.all() or user == self.user

    @property
    def join_template(self):
        if self.approved:
            return 'libraryauth/' + self.backend + '_join.html'
        return 'libraryauth/unapproved.html'

    @property
    def help_template(self):
        return 'libraryauth/' + self.backend + '_help.html'

    def get_absolute_url(self):
        return reverse('library', args=[self.user.username])

def add_group(sender, created, instance, **kwargs):
    if created:
        num = ''
        while created:
            (group, created) = Group.objects.get_or_create(name=instance.user.username + num)
            # make sure not using a group twice!
            if created:
                created = False
            else:
                num += '+'
                try:
                    group.library
                    created = True
                except Library.DoesNotExist:
                    pass
        instance.group = group
        instance.save()

post_save.connect(add_group, sender=Library)

def ip_to_long(value):
    validators.validate_ipv4_address(value)

    lower_validator = validators.MinValueValidator(0)
    upper_validator = validators.MinValueValidator(255)

    value = value.split('.')
    output = 0

    for i in range(0, 4):
        validators.validate_integer(value[i])
        lower_validator(value[i])
        upper_validator(value[i])
        output += long(value[i]) * (256**(3-i))

    return output

def long_to_ip(value):
    validators.validate_integer(value)
    value = long(value)

    validators.MinValueValidator(0)(value)
    validators.MaxValueValidator(4294967295)(value)

    return '%d.%d.%d.%d' % (value >> 24, value >> 16 & 255,
                            value >> 8 & 255, value & 255)

class IP(object):
    def __init__(self, value):
        self.int = value

    def _set_int(self, value):
        if isinstance(value, IP):
            self._int = IP.int

        try:
            self._int = long(value)
        except ValueError:
            self._int = ip_to_long(value)
        except (TypeError, ValidationError):
            self._int = None

    def _get_int(self):
        return self._int

    int = property(_get_int, _set_int)

    def _get_str(self):
        if self.int != None:
            return long_to_ip(self.int)
        return ''

    string = property(_get_str, _set_int)

    def __eq__(self, other):
        if not isinstance(other, IP):
            try:
                other = IP(other)
            except:
                return False

        return self.int == other.int

    def __cmp__(self, other):
        if not isinstance(other, IP):
            other = IP(other)

        if self.int is not None and other.int is not None:
            return self.int.__cmp__(other.int)

        raise ValueError('Invalid arguments')

    def __unicode__(self):
        return self.string

    def __str__(self):
        return self.string

class IPAddressFormField(BaseIPAddressField):
    default_validators = []

    def prepare_value(self, value):
        if isinstance(value, IP):
            return value.string

        try:
            return IP(value).string
        except:
            pass

        return value

    def to_python(self, value):
        if value == 0:
            return IP(0)
        if value in validators.EMPTY_VALUES:
            return None

        try:
            return IP(value)
        except ValidationError:
            raise ValidationError(self.default_error_messages['invalid'],
                                  code='invalid')

class IPAddressModelField(models.GenericIPAddressField):
    empty_strings_allowed = False

    def __init__(self, *args, **kwargs):
        models.Field.__init__(self, *args, **kwargs)

    def get_internal_type(self):
        return "PositiveIntegerField"

    def get_prep_value(self, value):
        if not value:
            return value

        if isinstance(value, IP):
            return value.int

    def to_python(self, value):
        if isinstance(value, IP):
            return value
        try:
            return IP(value)
        except ValidationError:
            return None

    def formfield(self, **kwargs):
        defaults = {'form_class': IPAddressFormField}
        defaults.update(kwargs)
        return super(models.GenericIPAddressField, self).formfield(**defaults)

    def deconstruct(self):
        name, path, args, kwargs = super(models.GenericIPAddressField, self).deconstruct()
        return name, path, args, kwargs


class Block(models.Model):
    library = models.ForeignKey(Library, on_delete=models.CASCADE, related_name='ip_auths')
    lower = IPAddressModelField(db_index=True, unique=True)
    upper = IPAddressModelField(db_index=True, blank=True, null=True)

    def clean(self):
        if self.upper and self.upper.int:
            try:
                if self.lower > self.upper:
                    raise ValidationError('Lower end of the Block must be less '
                                          'than or equal to the upper end')
            except ValueError, e:
                pass


    def __unicode__(self):
        if self.upper and self.upper.int:
            return u'%s %s-%s' % (self.library, self.lower, self.upper)
        return u'%s %s' % (self.library, self.lower)

    class Meta:
        ordering = ['lower',]


# from https://en.wikipedia.org/wiki/Luhn_algorithm#Implementation_of_standard_Mod_10
def luhn_checksum(card_number):
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = 0
    checksum += sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d*2))
    return checksum % 10

class CardPattern(models.Model):
    library = models.ForeignKey(Library, on_delete=models.CASCADE, related_name='cardnum_auths')
    # match pattern ^\d+#+$
    pattern = models.CharField(max_length=20)
    checksum = models.BooleanField(default=True)

    def is_valid(self, card_number):
        match_pattern = '^' + self.pattern.replace('#', r'\d', 20) + '$'
        if re.match(match_pattern, card_number) is None:
            return False
        if self.checksum:
            return luhn_checksum(card_number) == 0
        return True

class LibraryUser(models.Model):
    library = models.ForeignKey(Library, on_delete=models.CASCADE, related_name='library_users')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_libraries',
    )
    credential = models.CharField(max_length=30, null=True)
    date_modified = models.DateTimeField(auto_now=True)

class EmailPattern(models.Model):
    library = models.ForeignKey(Library, on_delete=models.CASCADE, related_name='email_auths')
    # email endswith string
    pattern = models.CharField(max_length=20)

    def is_valid(self, email):
        return email.lower().endswith(self.pattern.lower())
