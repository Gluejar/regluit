from django.contrib.auth.models import User
from django.contrib.admin import ModelAdmin
from django.contrib.admin.sites import AdminSite

from regluit.core import models


class RegluitAdmin(AdminSite):
    password_change_template = 'registration/password_change_form'

class UserAdmin(ModelAdmin):
    pass

class ClaimAdmin(ModelAdmin):
    date_hierarchy = 'created'

class RightsHolderAdmin(ModelAdmin):
    date_hierarchy = 'created'

class PremiumAdmin(ModelAdmin):
    date_hierarchy = 'created'

class CampaignAdmin(ModelAdmin):
    date_hierarchy = 'created'

class WorkAdmin(ModelAdmin):
    search_fields = ('title',)
    ordering = ('title',)
    list_display = ('title', 'created')
    date_hierarchy = 'created'
    fields = ('title',)

class AuthorAdmin(ModelAdmin):
    date_hierarchy = 'created'

class SubjectAdmin(ModelAdmin):
    date_hierarchy = 'created'
    ordering = ('name',)

class EditionAdmin(ModelAdmin):
    list_display = ('title', 'publisher', 'created')
    date_hierarchy = 'created'
    ordering = ('title',)

class EbookAdmin(ModelAdmin):
    date_hierarchy = 'created'
    ordering = ('edition__title',)

class WishlistAdmin(ModelAdmin):
    date_hierarchy = 'created'

class UserProfileAdmin(ModelAdmin):
    date_hierarchy = 'created'

admin_site = RegluitAdmin("Admin")

# need to figure out how to enable this without stomping on 
# /accounts/password/change/
# admin_site.register(models.User, UserAdmin)

admin_site.register(models.Work, WorkAdmin)
admin_site.register(models.Claim, ClaimAdmin)
admin_site.register(models.RightsHolder, RightsHolderAdmin)
admin_site.register(models.Premium, PremiumAdmin)
admin_site.register(models.Campaign, CampaignAdmin)
admin_site.register(models.Author, AuthorAdmin)
admin_site.register(models.Subject, SubjectAdmin)
admin_site.register(models.Edition, EditionAdmin)
admin_site.register(models.Ebook, EbookAdmin)
admin_site.register(models.Wishlist, WishlistAdmin)
admin_site.register(models.UserProfile, UserProfileAdmin)
