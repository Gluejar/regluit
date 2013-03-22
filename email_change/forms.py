# -*- coding: utf-8 -*-
#
#  This file is part of django-email-change.
#
#  django-email-change adds support for email address change and confirmation.
#
#  Development Web Site:
#    - http://www.codetrax.org/projects/django-email-change
#  Public Source Code Repository:
#    - https://source.codetrax.org/hgroot/django-email-change
#
#  Copyright 2010 George Notaras <gnot [at] g-loaded.eu>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

from django import forms
from django.db.models.loading import cache
from django.utils.translation import ugettext_lazy as _


class EmailChangeForm(forms.Form):
    
    email = forms.EmailField(label='New E-mail', max_length=75)
    
    def __init__(self, username=None, *args, **kwargs):
        """Constructor.
        
        **Mandatory arguments**
        
        ``username``
            The username of the user that requested the email change.
        
        """
        self.username = username
        super(EmailChangeForm, self).__init__(*args, **kwargs)
    
    def clean_email(self):
        """Checks whether the new email address differs from the user's current
        email address.
        
        """
        email = self.cleaned_data.get('email')
        
        User = cache.get_model('auth', 'User')
        user = User.objects.get(username__exact=self.username)
        
        # Check if the new email address differs from the current email address.
        if user.email == email:
            raise forms.ValidationError(_("Your email is already ")+ email)

        users = User.objects.exclude(id=user.id).filter(email__iexact=email)
        for user in users:
            raise forms.ValidationError(_("Another user with that email already exists."))
       
        return email

    oldemail = None
    


