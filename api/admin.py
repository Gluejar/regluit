from django.contrib.admin import ModelAdmin, site
from .models import AllowedRepo


class AllowedRepoAdmin(ModelAdmin):
    list_display = ('org', 'repo_name')

site.register(AllowedRepo, AllowedRepoAdmin)
