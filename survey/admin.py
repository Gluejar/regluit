from django.contrib import admin
from .models import Landing

# new in dj1.7
# @admin.register(Landing)
class LandingAdmin(admin.ModelAdmin):
    pass
    
