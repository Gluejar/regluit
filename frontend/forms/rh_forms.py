from django import forms

from regluit.core.models import RightsHolder, Claim

class RightsHolderForm(forms.ModelForm):
    email = forms.EmailField(
        help_text='notification email address for rights holder',
        max_length=100,
        error_messages={
                'required': 'Please enter a contact email address for the rights holder.'
            },
    )
    use4both = forms.BooleanField(label='use business address as mailing address', required=False)
    def clean_rights_holder_name(self):
        rights_holder_name = self.data["rights_holder_name"]
        try:
            RightsHolder.objects.get(rights_holder_name__iexact=rights_holder_name)
        except RightsHolder.DoesNotExist:
            return rights_holder_name
        raise forms.ValidationError('Another rights holder with that name already exists.')

    class Meta:
        model = RightsHolder
        exclude = ('approved', 'signer_ip')
        widgets = {
            'address': forms.Textarea(attrs={'rows': 4}),
            'mailing': forms.Textarea(attrs={'rows': 4}),
            'owner': forms.HiddenInput()
        }
        help_texts = {
            'signature': 'Type your name to enter your electronic signature.',
            'rights_holder_name':  'Enter the rights holder\'s legal name.',
        }
        error_messages = {
            'address': {
                'required': 'A business address for the rights holder is required.'
                },
            'mailing': {
                'required': 'Enter a mailing address for the rights holder, if different from the \
                             business address.'
            },
            'rights_holder_name': {
                'required': 'Enter the rights holder\'s legal name.'
            },
            'signature': {
                'required': 'Type your name to enter your electronic signature.'
            },
            'signer': {
                'required': 'Please enter the name of the person signing on behalf of the rights \
                             holder.'
            },
            'signer_title': {
                'required': 'Please enter the signer\'s title. (Use \'self\' if you are \
                             personally the rights holder.)'
            },
        }

class UserClaimForm (forms.ModelForm):
    i_agree = forms.BooleanField(
            error_messages={'required': 'You must agree to the Terms in order to claim a work.'}
        )

    def __init__(self, user_instance, *args, **kwargs):
        super(UserClaimForm, self).__init__(*args, **kwargs)
        self.fields['rights_holder'] = forms.ModelChoiceField(
            queryset=user_instance.rights_holder.filter(approved=False),
            empty_label=None,
        )

    def clean_work(self):
        work = self.cleaned_data.get('work', None)
        if not work:
            try:
                workids = self.data['claim-work']
                if workids:
                    work = models.WasWork.objects.get(was = workids[0]).work
                else:
                    raise forms.ValidationError('That work does not exist.')
            except models.WasWork.DoesNotExist:
                raise forms.ValidationError('That work does not exist.')
        return work

    class Meta:
        model = Claim
        exclude = ('status',)
        widgets = {
                'user': forms.HiddenInput,
                'work': forms.HiddenInput,
        }

