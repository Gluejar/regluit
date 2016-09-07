"""
django imports
"""
from django import forms
from django.contrib.admin import ModelAdmin, site
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User

"""
regluit imports
"""

site.login_template = 'registration/login.html'
    
class UserAdmin(ModelAdmin):
    search_fields = ['username', 'email']
    list_display = ('username', 'email')

    

site.unregister(User)
site.register(User, UserAdmin)

