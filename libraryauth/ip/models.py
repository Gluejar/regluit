from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core import validators
from django.db import models
from django.db.models import Q
from django.forms import IPAddressField as BaseIPAddressField
from django.utils.translation import ugettext_lazy as _



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
        output += int(value[i]) * (256**(3-i))

    return output

def long_to_ip(value):
    validators.validate_integer(value)
    value = int(value)

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
            self._int = int(value)
        except ValueError:
            self._int = ip_to_long(value)
        except (TypeError, ValidationError):
            self._int = None

    def _get_int(self):
        return self._int

    int = property(_get_int, _set_int)

    def _get_str(self):
        if self.int:
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

        if self.int and other.int:
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
        if value in validators.EMPTY_VALUES:
            return None

        try:
            return IP(value)
        except ValidationError:
            raise ValidationError(self.default_error_messages['invalid'],
                                  code='invalid')

class IPAddressModelField(models.IPAddressField):
    __metaclass__ = models.SubfieldBase
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
        return super(models.IPAddressField, self).formfield(**defaults)


class Range(models.Model):
    user = models.ForeignKey(User, related_name='+')
    lower = IPAddressModelField(db_index=True, unique=True)
    upper = IPAddressModelField(db_index=True, blank=True, null=True)

    def clean(self):
        if self.upper and self.upper.int:
            try:
                if self.lower >= self.upper:
                    raise ValidationError('Lower end of the range must be less '
                                          'than the upper end')
            except ValueError, e:
                pass

        others = Range.objects.exclude(pk=self.pk)
        query = Q(lower__lte=self.lower, upper__gte=self.lower) | \
                Q(lower=self.lower)
        if self.upper and self.upper.int:
            textual = u'%s-%s' % (self.lower, self.upper)
            query = query | Q(lower__range=(self.lower, self.upper)) | \
                    Q(lower__lte=self.upper, upper__gte=self.upper)
        else:
            textual = str(self.lower)

        query = others.filter(query)

        if query.exists():
            values = query.distinct().values_list('user__username', flat=True)
            raise ValidationError('%s overlaps a range in in use by: %s' % (textual,
                ', '.join(list(frozenset(values))[:5])))


    def __unicode__(self):
        if self.upper and self.upper.int:
            return u'%s %s-%s' % (self.user.get_full_name(), self.lower,
                                  self.upper)
        return u'%s %s' % (self.user.get_full_name(), self.lower)

    class Meta:
        ordering = ['lower',]