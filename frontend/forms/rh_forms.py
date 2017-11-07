from django import forms

from regluit.core.models import RightsHolder

class RightsHolderForm(forms.ModelForm):
    email = forms.EmailField(
        help_text='notification email address for rights holder',
        max_length=100,
        error_messages={
                'required': 'Please enter a contact email address for the rights holder.'
            },
    )
    use4both = forms.BooleanField(label='use business address as mailing address')
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

'''class RightsHolderApprovalForm(RightsHolderForm):
    owner = AutoCompleteSelectField(
            OwnerLookup,
            label='Owner',
            widget=AutoCompleteSelectWidget(OwnerLookup),
            required=True,
    )
'''
