from django.contrib import admin
from django.urls import reverse
from .models import Landing

adminsite = admin.site

    
from django.contrib import admin

# new in dj1.7
# @admin.register(Landing)
class LandingAdmin(admin.ModelAdmin):
    list_display = ('label', 'content_type', 'object_id', )
    ordering = [ 'object_id', ]


adminsite.register(Landing, LandingAdmin)

