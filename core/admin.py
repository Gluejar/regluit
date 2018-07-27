#
#django imports
#
from django import forms
from django.contrib.admin import ModelAdmin, register
from django.urls import reverse

from selectable.forms import (
    AutoCompleteSelectWidget,
    AutoCompleteSelectField,
    AutoCompleteSelectMultipleWidget,
    AutoCompleteSelectMultipleField,
)

#
# regluit imports
#"""
from .lookups import (
    PublisherNameLookup,
    WorkLookup,
    OwnerLookup,
    EditionLookup,
    EbookLookup,
)
from . import models

class ClaimAdminForm(forms.ModelForm):
    work = AutoCompleteSelectField(
        lookup_class=WorkLookup,
        widget=AutoCompleteSelectWidget(lookup_class=WorkLookup),
        required=True,
    )
    user = AutoCompleteSelectField(
        lookup_class=OwnerLookup,
        widget=AutoCompleteSelectWidget(lookup_class=OwnerLookup),
        required=True,
    )
    class Meta(object):
        model = models.Claim
        exclude = ()

@register(models.Claim)
class ClaimAdmin(ModelAdmin):
    list_display = ('work', 'rights_holder', 'status')
    date_hierarchy = 'created'
    form = ClaimAdminForm

class RightsHolderAdminForm(forms.ModelForm):
    owner = AutoCompleteSelectField(
        lookup_class=OwnerLookup,
        widget=AutoCompleteSelectWidget(lookup_class=OwnerLookup),
        required=True,
    )
    class Meta(object):
        model = models.RightsHolder
        exclude = ()

@register(models.RightsHolder)
class RightsHolderAdmin(ModelAdmin):
    date_hierarchy = 'created'
    form = RightsHolderAdminForm

@register(models.Acq)
class AcqAdmin(ModelAdmin):
    readonly_fields = ('work', 'user', 'lib_acq', 'watermarked')
    search_fields = ['user__username']
    date_hierarchy = 'created'

@register(models.Premium)
class PremiumAdmin(ModelAdmin):
    list_display = ('campaign', 'amount', 'description')
    date_hierarchy = 'created'
    fields = ('type', 'amount', 'description', 'limit')

class CampaignAdminForm(forms.ModelForm):
    managers = AutoCompleteSelectMultipleField(
        lookup_class=OwnerLookup,
        widget=AutoCompleteSelectMultipleWidget(lookup_class=OwnerLookup),
        required=True,
    )
    class Meta(object):
        model = models.Campaign
        fields = (
            'managers', 'name', 'description', 'details', 'license', 'paypal_receiver',
            'status', 'type', 'email', 'do_watermark', 'use_add_ask', 'charitable',
        )

@register(models.Campaign)
class CampaignAdmin(ModelAdmin):
    list_display = ('work', 'created', 'status')
    date_hierarchy = 'created'
    search_fields = ['work']
    form = CampaignAdminForm

@register(models.Work)
class WorkAdmin(ModelAdmin):
    search_fields = ['title']
    ordering = ('title',)
    list_display = ('title', 'created')
    date_hierarchy = 'created'
    fields = ('title', 'description', 'language', 'featured', 'publication_range',
              'age_level', 'openlibrary_lookup')

@register(models.Author)
class AuthorAdmin(ModelAdmin):
    search_fields = ('name',)
    date_hierarchy = 'created'
    ordering = ('name',)
    exclude = ('editions',)

subject_authorities = (
    ('', 'keywords'),
    ('lcsh', 'LC subjects'),
    ('lcc', 'LC classifications'),
    ('bisacsh', 'BISAC heading'),
)

class SubjectAdminForm(forms.ModelForm):
    authority = forms.ChoiceField(choices=subject_authorities, required=False)
    class Meta(object):
        model = models.Subject
        fields = 'name', 'authority', 'is_visible'

@register(models.Subject)
class SubjectAdmin(ModelAdmin):
    search_fields = ('name',)
    date_hierarchy = 'created'
    ordering = ('name',)
    form = SubjectAdminForm

class EditionAdminForm(forms.ModelForm):
    work = AutoCompleteSelectField(
        lookup_class=WorkLookup,
        label='Work',
        widget=AutoCompleteSelectWidget(lookup_class=WorkLookup),
        required=True,
    )
    publisher_name = AutoCompleteSelectField(
        lookup_class=PublisherNameLookup,
        label='Publisher Name',
        widget=AutoCompleteSelectWidget(lookup_class=PublisherNameLookup),
        required=False,
    )
    class Meta(object):
        model = models.Edition
        exclude = ()

@register(models.Edition)
class EditionAdmin(ModelAdmin):
    list_display = ('title', 'publisher_name', 'created')
    date_hierarchy = 'created'
    ordering = ('title',)
    form = EditionAdminForm

class PublisherAdminForm(forms.ModelForm):
    name = AutoCompleteSelectField(
        lookup_class=PublisherNameLookup,
        label='Name',
        widget=AutoCompleteSelectWidget(lookup_class=PublisherNameLookup),
        required=True,
    )

    class Meta(object):
        model = models.Publisher
        exclude = ()

@register(models.Publisher)
class PublisherAdmin(ModelAdmin):
    list_display = ('name', 'url', 'logo_url', 'description')
    ordering = ('name',)
    form = PublisherAdminForm

@register(models.PublisherName)
class PublisherNameAdmin(ModelAdmin):
    list_display = ('name', 'publisher')
    ordering = ('name',)
    search_fields = ['name']

@register(models.Relation)
class RelationAdmin(ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ['name']

class EbookAdminForm(forms.ModelForm):
    edition = AutoCompleteSelectField(
        lookup_class=EditionLookup,
        label='Edition',
        widget=AutoCompleteSelectWidget(lookup_class=EditionLookup, attrs={'size':60}),
        required=True,
    )
    class Meta(object):
        model = models.Ebook
        exclude = ('user', 'filesize', 'download_count')

@register(models.Ebook)
class EbookAdmin(ModelAdmin):
    form = EbookAdminForm
    search_fields = ('edition__title', '^url')  # search by provider using leading url
    list_display = ('__unicode__', 'created', 'user', 'edition')
    date_hierarchy = 'created'
    ordering = ('edition__title',)
    readonly_fields = ('user', 'filesize', 'download_count')

class EbookFileAdminForm(forms.ModelForm):
    edition = AutoCompleteSelectField(
        lookup_class=EditionLookup,
        label='Edition',
        widget=AutoCompleteSelectWidget(lookup_class=EditionLookup, attrs={'size':60}),
        required=True,
    )
    ebook = AutoCompleteSelectField(
        lookup_class=EbookLookup,
        label='Ebook',
        widget=AutoCompleteSelectWidget(lookup_class=EbookLookup, attrs={'size':60}),
        required=False,
    )
    class Meta(object):
        model = models.EbookFile
        fields = ('file', 'format', 'edition', 'ebook', 'source')

@register(models.EbookFile)
class EbookFileAdmin(ModelAdmin):
    form = EbookFileAdminForm
    search_fields = ('ebook__edition__title', 'source')  # search by provider using leading url
    list_display = ('created', 'format', 'ebook_link', 'asking')
    date_hierarchy = 'created'
    ordering = ('edition__work',)
    fields = ('file', 'format', 'edition', 'edition_link', 'ebook', 'ebook_link', 'source')
    readonly_fields = ('file', 'edition_link', 'ebook_link',)
    def edition_link(self, obj):
        if obj.edition:
            link = reverse("admin:core_edition_change", args=[obj.edition_id])
            return u'<a href="%s">%s</a>' % (link, obj.edition)
        return u''
    def ebook_link(self, obj):
        if obj.ebook:
            link = reverse("admin:core_ebook_change", args=[obj.ebook_id])
            return u'<a href="%s">%s</a>' % (link, obj.ebook)
        return u''
    edition_link.allow_tags = True
    ebook_link.allow_tags = True


@register(models.Wishlist)
class WishlistAdmin(ModelAdmin):
    date_hierarchy = 'created'

@register(models.UserProfile)
class UserProfileAdmin(ModelAdmin):
    search_fields = ('user__username',)
    date_hierarchy = 'created'
    exclude = ('user',)

@register(models.Gift)
class GiftAdmin(ModelAdmin):
    list_display = ('to', 'acq_admin_link', 'giver',)
    search_fields = ('giver__username', 'to')
    readonly_fields = ('giver', 'acq',)
    def acq_admin_link(self, gift):
        return "<a href='/admin/core/acq/%s/'>%s</a>" % (gift.acq_id, gift.acq)
    acq_admin_link.allow_tags = True

@register(models.CeleryTask)
class CeleryTaskAdmin(ModelAdmin):
    pass

@register(models.Press)
class PressAdmin(ModelAdmin):
    list_display = ('title', 'source', 'date')
    ordering = ('-date',)

class WorkRelationAdminForm(forms.ModelForm):
    to_work = AutoCompleteSelectField(
        lookup_class=WorkLookup,
        label='To Work',
        widget=AutoCompleteSelectWidget(lookup_class=WorkLookup),
        required=True,
    )
    from_work = AutoCompleteSelectField(
        lookup_class=WorkLookup,
        label='From Work',
        widget=AutoCompleteSelectWidget(lookup_class=WorkLookup),
        required=True,
    )
    class Meta(object):
        model = models.WorkRelation
        exclude = ()

@register(models.WorkRelation)
class WorkRelationAdmin(ModelAdmin):
    form = WorkRelationAdminForm
    list_display = ('to_work', 'relation', 'from_work')

class IdentifierAdminForm(forms.ModelForm):
    work = AutoCompleteSelectField(
        lookup_class=WorkLookup,
        label='Work',
        widget=AutoCompleteSelectWidget(lookup_class=WorkLookup, attrs={'size':60}),
        required=False,
    )
    edition = AutoCompleteSelectField(
        lookup_class=EditionLookup,
        label='Edition',
        widget=AutoCompleteSelectWidget(lookup_class=EditionLookup, attrs={'size':60}),
        required=False,
    )
    class Meta(object):
        model = models.Identifier
        exclude = ()

@register(models.Identifier)
class IdentifierAdmin(ModelAdmin):
    form = IdentifierAdminForm
    list_display = ('type', 'value')
    search_fields = ('type', 'value')

@register(models.Offer)
class OfferAdmin(ModelAdmin):
    list_display = ('work', 'license', 'price', 'active')
    search_fields = ('work__title',)
    readonly_fields = ('work',)
