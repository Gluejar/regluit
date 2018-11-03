#external library imports

import logging
import re
import unicodedata

from datetime import date
from decimal import Decimal as D

#django imports

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.forms.widgets import RadioSelect, SelectDateWidget
from django.utils.translation import ugettext_lazy as _

from selectable.forms import (
    AutoCompleteSelectWidget,
    AutoCompleteSelectField
)

#regluit imports

from regluit.core.models import (
    UserProfile,
    RightsHolder,
    Claim,
    Campaign,
    Identifier,
    Offer,
    Premium,
    Ebook,
    EbookFile,
    Edition,
    PledgeExtra,
    Work,
    Press,
    Libpref,
    TWITTER,
    FACEBOOK,
    UNGLUEITAR
)
from regluit.libraryauth.models import Library
from regluit.core.parameters import (
    LIBRARY,
    REWARDS,
    BUY2UNGLUE,
    THANKS,
)
from regluit.core.lookups import (
    OwnerLookup,
    WorkLookup,
    SubjectLookup,
)
from regluit.core.validation import test_file
from regluit.utils.fields import ISBNField


from .bibforms import EditionForm, IdentifierForm
from .rh_forms import (
    CCDateForm,
    CloneCampaignForm,
    date_selector,
    DateCalculatorForm,
    EditManagersForm,
    ManageCampaignForm,
    OpenCampaignForm,
    RightsHolderForm,
    UserClaimForm
)
from questionnaire.models import Questionnaire

logger = logging.getLogger(__name__)

class SurveyForm(forms.Form):
    label = forms.CharField(max_length=64, required=True)
    survey = forms.ModelChoiceField(Questionnaire.objects.all(), widget=RadioSelect(), empty_label=None, required = True,)
    isbn = ISBNField(
        label=_("ISBN"),
        max_length=17,
        required = False,
        help_text = _("13 digits, no dash."),
        error_messages = {
            'invalid': _("This must be a valid ISBN-13."),
        }
    )

    def clean_isbn(self):
        isbn = self.cleaned_data['isbn']
        if not isbn:
            return ''
        try:
            self.work = Identifier.objects.get(type='isbn', value=isbn).work
            return isbn
        except Identifier.DoesNotExist:
            self.work = None
            raise forms.ValidationError( 'That ISBN is not in our database')

class EbookFileForm(forms.ModelForm):
    file = forms.FileField(max_length=16777216)
    version_label = forms.CharField(max_length=512, required=False)
    new_version_label = forms.CharField(required=False)

    def __init__(self, campaign_type=BUY2UNGLUE, *args, **kwargs):
        super(EbookFileForm, self).__init__(*args, **kwargs)
        self.campaign_type = campaign_type
        if campaign_type == BUY2UNGLUE:
            self.fields['format'].widget = forms.HiddenInput()
        if campaign_type == THANKS:
            self.fields['format'].widget = forms.Select(
                choices = (('pdf', 'PDF'), ('epub', 'EPUB'), ('mobi', 'MOBI'))
            )

    def clean_version_label(self):
        new_label = self.data.get('new_version_label','')
        return new_label if new_label else self.cleaned_data['version_label']

    def clean_format(self):
        if self.campaign_type is BUY2UNGLUE:
            return 'epub'
        else:
            logger.info("EbookFileForm "+self.cleaned_data.get('format',''))
            return self.cleaned_data.get('format','')

    def clean(self):
        fformat = self.cleaned_data['format']
        the_file = self.cleaned_data.get('file', None)
        test_file(the_file, fformat)
        return self.cleaned_data

    class Meta:
        model = EbookFile
        widgets = { 'edition': forms.HiddenInput}
        fields = ('file', 'format', 'edition')

class EbookForm(forms.ModelForm):
    file = forms.FileField(max_length=16777216, required=False)
    url = forms.CharField(required=False, widget=forms.TextInput(attrs={'size' : 60},))
    version_label = forms.CharField(required=False)
    new_version_label = forms.CharField(required=False)

    class Meta:
        model = Ebook
        #exclude = ('created', 'download_count', 'active', 'filesize', 'version_iter')
        fields = ('url', 'format', 'provider', 'version_label', 'rights', 'edition', 'user')
        widgets = {
                'edition': forms.HiddenInput,
                'user': forms.HiddenInput,
                'provider': forms.HiddenInput,
            }
    def clean_version_label(self):
        new_label = self.data.get('new_version_label','')
        return new_label if new_label else self.cleaned_data['version_label']

    def set_provider(self):
        url = self.cleaned_data['url']
        new_provider = Ebook.infer_provider(url)
        if url and not new_provider:
            raise forms.ValidationError(_("At this time, ebook URLs must point at Internet Archive, Wikisources, Wikibooks, Hathitrust, Project Gutenberg, raw files at Github, Google Books, or OApen."))
        self.cleaned_data['provider'] = new_provider if new_provider else "Unglue.it"

    def clean_url(self):
        url = self.cleaned_data['url']
        try:
            Ebook.objects.get(url=url)
        except Ebook.DoesNotExist:
            return url
        raise forms.ValidationError(_("There's already an ebook with that url."))

    def clean(self):
        self.set_provider()
        format = self.cleaned_data.get('format', '')
        the_file = self.cleaned_data.get('file', None)
        url = self.cleaned_data.get('url', None)
        test_file(the_file, format)
        if not the_file and not url:
            raise forms.ValidationError(_("Either a link or a file is required."))
        if the_file and url:
            self.cleaned_data['url'] = ''
        return self.cleaned_data

class ProfileForm(forms.ModelForm):
    clear_facebook = forms.BooleanField(required=False)
    clear_twitter = forms.BooleanField(required=False)
    clear_goodreads = forms.BooleanField(required=False)

    class Meta:
        model = UserProfile
        fields = 'tagline', 'librarything_id', 'facebook_id', 'home_url', 'clear_facebook', 'clear_twitter', 'clear_goodreads', 'avatar_source'
        widgets = {
            'tagline': forms.Textarea(attrs={'rows': 5, 'onKeyUp': "counter(this, 140)", 'onBlur': "counter(this, 140)"}),
        }

    def __init__(self, *args, **kwargs):
        profile = kwargs.get('instance')
        super(ProfileForm, self).__init__(*args, **kwargs)
        choices = []
        for choice in self.fields['avatar_source'].choices :
            if choice[0] == TWITTER and not profile.pic_url:
                pass
            else:
                choices.append(choice)
        self.fields['avatar_source'].choices = choices

def getTransferCreditForm(maximum, data=None, *args, **kwargs ):
    class TransferCreditForm(forms.Form):
        recipient = AutoCompleteSelectField(
                OwnerLookup,
                label='Recipient',
                widget=AutoCompleteSelectWidget(OwnerLookup),
                required=True,
                error_messages={'required': 'Please ensure the recipient is a valid Unglue.it account.'},
            )
        amount = forms.IntegerField(
                required=True,
                min_value=1,
                max_value=maximum,
                label="Transfer Amount",
                error_messages={
                    'min_value': 'Transfer amount must be positive',
                    'max_value': 'You only have %(limit_value)s available for transfer'
                },
            )
    return TransferCreditForm( data=data )


class WorkForm(forms.Form):
    other_work = forms.ModelChoiceField(queryset=Work.objects.all(),
            widget=forms.HiddenInput(),
            required=True,
            error_messages={'required': 'Missing work to merge with.'},
            )
    work = None

    def clean_other_work(self):
        if self.cleaned_data["other_work"].id == self.work.id:
            raise forms.ValidationError(_("You can't merge a work into itself"))
        return self.cleaned_data["other_work"]

    def __init__(self, work=None, *args, **kwargs):
        super(WorkForm, self).__init__(*args, **kwargs)
        self.work = work

class OtherWorkForm(WorkForm):
    other_work = AutoCompleteSelectField(
            WorkLookup,
            label='Other Work (title)',
            widget=AutoCompleteSelectWidget(WorkLookup),
            required=True,
            error_messages={'required': 'Missing work to merge with.'},
        )

    def __init__(self,  *args, **kwargs):
        super(OtherWorkForm, self).__init__(*args, **kwargs)
        self.fields['other_work'].widget.update_query_parameters({'language':self.work.language})

class CustomPremiumForm(forms.ModelForm):

    class Meta:
        model = Premium
        fields = 'campaign', 'amount', 'description', 'type', 'limit'
        widgets = {
                'description': forms.Textarea(attrs={'cols': 80, 'rows': 4}),
                'campaign': forms.HiddenInput,
                'type': forms.HiddenInput(attrs={'value':'XX'}),
                'limit': forms.TextInput(attrs={'value':'0'}),
            }
    def clean_type(self):
        return 'CU'

class OfferForm(forms.ModelForm):

    class Meta:
        model = Offer
        fields = 'work', 'price', 'license'
        widgets = {
                'work': forms.HiddenInput,
                'license': forms.HiddenInput,
            }


class CampaignPurchaseForm(forms.Form):
    anonymous = forms.BooleanField(required=False, label=_("Make this purchase anonymous, please"))
    offer_id = forms.IntegerField(required=False)
    offer = None
    library_id = forms.IntegerField(required=False)
    library = None
    copies = forms.IntegerField(required=False, min_value=1)
    give_to = forms.EmailField(required = False)
    give_message = forms.CharField(required = False, max_length=512,  )

    def clean_offer_id(self):
        offer_id = self.cleaned_data['offer_id']
        try:
            self.offer = Offer.objects.get(id=offer_id)
        except  Offer.DoesNotExist:
            raise forms.ValidationError(_("Sorry, that offer is not valid."))

    def clean_library_id(self):
        library_id = self.cleaned_data['library_id']
        if library_id:
            try:
                self.library = Library.objects.get(id=library_id)
            except  Library.DoesNotExist:
                raise forms.ValidationError(_("Sorry, that Library is not valid."))

    def clean_copies(self):
        copies = self.cleaned_data.get('copies', 1)
        return copies if copies else 1

    def clean_anonymous(self):
        if self.data.get('give', False):
            return True
        else:
            return self.cleaned_data['anonymous']

    def clean(self):
        if self.offer.license == LIBRARY:
            if not self.library:
                raise forms.ValidationError(_("No library specified." ))
        if self.data.get('give', False):
            if not self.cleaned_data.get('give_to', None):
                raise forms.ValidationError(_("Gift recipient email is needed." ))
        else:
            if 'give_to' in self._errors:
                del self._errors['give_to']
        return self.cleaned_data

    def amount(self):

        return self.offer.price * self.cleaned_data.get('copies', 1) if self.offer else None

    @property
    def trans_extra(self):
        pe = PledgeExtra( anonymous=self.cleaned_data['anonymous'],
                            offer = self.offer )
        if self.library:
            pe.extra['library_id'] = self.library.id
        pe.extra['copies'] = self.cleaned_data.get('copies', 1)
        if self.data.get('give', False):
            pe.extra['give_to'] = self.cleaned_data['give_to']
            pe.extra['give_message'] = self.cleaned_data['give_message']
        return pe

class CampaignThanksForm(forms.Form):
    anonymous = forms.BooleanField(
        required=False,
        label=_("Make this contribution anonymous, please")
    )
    preapproval_amount = forms.DecimalField(
        required = True,
        min_value=D('1.00'),
        max_value=D('2000.00'),
        decimal_places=2,
        label="Pledge Amount",
    )
    @property
    def trans_extra(self):
        pe = PledgeExtra( anonymous=self.cleaned_data['anonymous'] )

class DonationForm(forms.Form):
    amount = forms.DecimalField(
        required = True,
        min_value=D('1.00'),
        max_value=D('20000.00'),
        decimal_places=2,
        label="Donation Amount",
    )


class CampaignPledgeForm(forms.Form):
    preapproval_amount = forms.DecimalField(
        required = False,
        min_value=D('1.00'),
        max_value=D('5000.00'),
        decimal_places=2,
        label="Support Amount",
    )
    def amount(self):
        return self.cleaned_data["preapproval_amount"] if self.cleaned_data else None

    anonymous = forms.BooleanField(required=False, label=_("Make this support anonymous, please"))
    ack_name = forms.CharField(
        required=False,
        max_length=64,
        label=_("What name should we display?")
    )
    ack_dedication = forms.CharField(required=False, max_length=140, label=_("Your dedication:"))

    premium_id = forms.IntegerField(required=False)
    donation = forms.BooleanField(required=False, label=_("Make this a donation, not a pledge."))
    premium = None

    @property
    def trans_extra(self):
        return PledgeExtra( anonymous=self.cleaned_data['anonymous'],
                            ack_name=self.cleaned_data['ack_name'],
                            ack_dedication=self.cleaned_data['ack_dedication'],
                            premium=self.premium)

    def clean_preapproval_amount(self):
        preapproval_amount = self.cleaned_data['preapproval_amount']
        if preapproval_amount is None:
            raise forms.ValidationError(_("Please enter a pledge amount."))
        return preapproval_amount

    def clean_premium_id(self):
        premium_id = self.cleaned_data['premium_id']
        try:
            self.premium = Premium.objects.get(id=premium_id)
            if self.premium.limit > 0:
                if self.premium.limit <= self.premium.premium_count:
                    raise forms.ValidationError(_("Sorry, that premium is fully subscribed."))
        except  Premium.DoesNotExist:
            raise forms.ValidationError(_("Sorry, that premium is not valid."))

    def clean(self):
        # check on whether the preapproval amount is < amount for premium tier. If so, put an error message
        preapproval_amount = self.cleaned_data.get("preapproval_amount")
        if preapproval_amount is None:
            # preapproval_amount failed validation, that error is the relevant one
            return self.cleaned_data
        elif self.premium is None:
            raise forms.ValidationError(_("Please select a premium." ))
        elif preapproval_amount < self.premium.amount:
            logger.info("raising form validating error")
            raise forms.ValidationError(_("Sorry, you must pledge at least $%s to select that premium." % (self.premium.amount)))
        donation = self.cleaned_data.get('donation', False)
        if donation and self.premium.amount > 0:
            raise forms.ValidationError(_("Sorry, donations are not eligible for premiums."))
        
        return self.cleaned_data

class TokenCCMixin(forms.Form):
    stripe_token = forms.CharField(required=True, widget=forms.HiddenInput())

class BaseCCMixin(forms.Form):
    work_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    preapproval_amount = forms.DecimalField(
        required=False,
        min_value=D('1.00'),
        max_value=D('100000.00'),
        decimal_places=2,
        label="Amount",
    )
class UserCCMixin(forms.Form):
    username = forms.CharField(max_length=30, required=True, widget=forms.HiddenInput())

class PlainCCForm(TokenCCMixin, forms.Form):
    pass

class BaseCCForm(BaseCCMixin, TokenCCMixin, forms.Form):
    pass

class AnonCCForm(BaseCCForm):
    email = forms.CharField(max_length=30, required=False, widget=forms.TextInput())

class CCForm(UserCCMixin, BaseCCForm):
    pass

class AccountCCForm( BaseCCMixin, UserCCMixin, forms.Form):
    pass

class GoodreadsShelfLoadingForm(forms.Form):
    goodreads_shelf_name_number = forms.CharField(widget=forms.Select(choices=(
                ('all','all'),
                )))

class LibraryThingForm(forms.Form):
    lt_username = forms.CharField(max_length=30, required=True)

class PledgeCancelForm(forms.Form):
    # which campaign whose active transaction to cancel?
    campaign_id = forms.IntegerField(required=True, widget=forms.HiddenInput())


class CampaignAdminForm(forms.Form):
    campaign_id = forms.IntegerField()

class EmailShareForm(forms.Form):
    recipient = forms.EmailField(error_messages={'required': 'Please specify a recipient.'})
    subject = forms.CharField(max_length=100, error_messages={'required': 'Please specify a subject.'})
    message = forms.CharField(
        widget=forms.Textarea(),
        error_messages={'required': 'Please include a message.'}
    )
    # allows us to return user to original page by passing it as hidden form input
    # we can't rely on POST or GET since the emailshare view handles both
    # and may iterate several times as it catches user errors, losing URL info
    next = forms.CharField(widget=forms.HiddenInput())

class FeedbackForm(forms.Form):
    sender = forms.EmailField(
        widget=forms.TextInput(attrs={'size':50}),
        label="Your email",
        error_messages={'required': 'Please specify your email address.'}
    )
    subject = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={'size':50}),
        error_messages={'required': 'Please specify a subject.'}
    )
    message = forms.CharField(
        widget=forms.Textarea(),
        error_messages={'required': 'Please specify a message.'}
    )
    page = forms.CharField(widget=forms.HiddenInput())
    notarobot = forms.IntegerField(
        label="Please prove you're not a robot",
        error_messages={'required': "You must do the sum to prove you're not a robot."}
    )
    answer = forms.IntegerField(widget=forms.HiddenInput())
    num1 = forms.IntegerField(widget=forms.HiddenInput())
    num2 = forms.IntegerField(widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = self.cleaned_data
        notarobot = str(cleaned_data.get("notarobot"))
        answer = str(cleaned_data.get("answer"))
        if notarobot != answer:
            raise forms.ValidationError(_("Whoops, try that sum again."))

        return cleaned_data

class MsgForm(forms.Form):
    msg = forms.CharField(
        widget=forms.Textarea(),
        error_messages={'required': 'Please specify a message.'}
    )

    def full_clean(self):
        super(MsgForm, self).full_clean()
        if self.data.has_key("supporter"):
            try:
                self.cleaned_data['supporter'] = User.objects.get(id=self.data["supporter"])
            except User.DoesNotExist:
                raise ValidationError("Supporter does not exist")
        else:
            raise ValidationError("Supporter is not specified")
        if self.data.has_key("work"):
            try:
                self.cleaned_data['work'] = Work.objects.get(id=self.data["work"])
            except Work.DoesNotExist:
                raise ValidationError("Work does not exist")
        else:
            raise ValidationError("Work is not specified")

class PressForm(forms.ModelForm):
    class Meta:
        model = Press
        exclude = ()

        widgets = {
                'date': SelectDateWidget(years=range(2010,2025)),
            }

class KindleEmailForm(forms.Form):
    kindle_email = forms.EmailField()


class LibModeForm(forms.ModelForm):
    class Meta:
        model = Libpref
        fields = ()

class RegiftForm(forms.Form):
    give_to = forms.EmailField(label="email address of recipient")
    give_message = forms.CharField(
        max_length=512,
        label="your gift message",
        initial="Here's an ebook from unglue.it, I hope you like it! - me",
    )

class SubjectSelectForm(forms.Form):
    add_kw = AutoCompleteSelectField(
            SubjectLookup,
            widget=AutoCompleteSelectWidget(SubjectLookup,allow_new=False),
            label='Keyword',
        )
class MapSubjectForm(forms.Form):
    subject = AutoCompleteSelectField(
            SubjectLookup,
            widget=AutoCompleteSelectWidget(SubjectLookup,allow_new=False),
            label='Source Subject',
        )
    onto_subject = AutoCompleteSelectField(
            SubjectLookup,
            widget=AutoCompleteSelectWidget(SubjectLookup,allow_new=False),
            label='Target Subject',
        )

