from django.contrib import admin
from .models import Target

# new in dj1.7
# @admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    pass
    
