from django import forms
from django.contrib.auth.models import User
from django.contrib.admin import ModelAdmin
from django.contrib.admin.sites import AdminSite

from selectable.forms import AutoCompleteSelectWidget,AutoCompleteSelectField


from regluit.core import models
from regluit import payment
from regluit.core.lookups import PublisherNameLookup

from djcelery.admin import TaskState, WorkerState, TaskMonitor, WorkerMonitor, \
      IntervalSchedule, CrontabSchedule, PeriodicTask, PeriodicTaskAdmin

from notification.admin import NoticeTypeAdmin, NoticeSettingAdmin, NoticeAdmin
from notification.models import NoticeType, NoticeSetting, Notice, ObservedItem, NoticeQueueBatch

import pickle

class RegluitAdmin(AdminSite):
    login_template = 'registration/login.html'

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
    ordering = ('name',)

class SubjectAdmin(ModelAdmin):
    date_hierarchy = 'created'
    ordering = ('name',)

class EditionAdmin(ModelAdmin):
    list_display = ('title', 'publisher_name', 'created')
    date_hierarchy = 'created'
    ordering = ('title',)

class PublisherAdminForm(forms.ModelForm):
    name = AutoCompleteSelectField(
            PublisherNameLookup,
            label='Name',
            widget=AutoCompleteSelectWidget(PublisherNameLookup),
            required=True,
        )

    class Meta(object):
        model = models.Publisher
        
class PublisherAdmin(ModelAdmin):
    list_display = ('name', 'url', 'logo_url', 'description')
    ordering = ('name',)
    form = PublisherAdminForm

class PublisherNameAdmin(ModelAdmin):
    list_display = ('name', 'publisher')
    ordering = ('name',)
    search_fields = ['name']
    
class EbookAdmin(ModelAdmin):
    search_fields = ('edition__title',)
    list_display = ('__unicode__','created', 'user','edition')
    date_hierarchy = 'created'
    ordering = ('edition__title',)
    exclude = ('edition','user')

class WishlistAdmin(ModelAdmin):
    date_hierarchy = 'created'

class UserProfileAdmin(ModelAdmin):
    date_hierarchy = 'created'
    
class CeleryTaskAdmin(ModelAdmin):
    pass

class TransactionAdmin(ModelAdmin):
    date_hierarchy = 'date_created'
    
class PaymentResponseAdmin(ModelAdmin):
    pass

class ReceiverAdmin(ModelAdmin):
    ordering = ('email',)    
    
def notice_queue_batch_data(obj):
    return pickle.loads(str(obj.pickled_data).decode("base64"))
notice_queue_batch_data.short_description = 'unpickled_data'

class NoticeQueueBatchAdmin(ModelAdmin):
    # show the pickled data in a form humans can parse more easily
    list_display = (notice_queue_batch_data,)
    pass
    
class PressAdmin(ModelAdmin):
    list_display = ('title', 'source', 'date')
    ordering = ('-date',)

admin_site = RegluitAdmin("Admin")

admin_site.register(User, UserAdmin)
admin_site.register(models.Work, WorkAdmin)
admin_site.register(models.Claim, ClaimAdmin)
admin_site.register(models.RightsHolder, RightsHolderAdmin)
admin_site.register(models.Premium, PremiumAdmin)
admin_site.register(models.Campaign, CampaignAdmin)
admin_site.register(models.Author, AuthorAdmin)
admin_site.register(models.Publisher, PublisherAdmin)
admin_site.register(models.PublisherName, PublisherNameAdmin)
admin_site.register(models.Subject, SubjectAdmin)
admin_site.register(models.Edition, EditionAdmin)
admin_site.register(models.Ebook, EbookAdmin)
admin_site.register(models.Wishlist, WishlistAdmin)
admin_site.register(models.UserProfile, UserProfileAdmin)
admin_site.register(models.CeleryTask, CeleryTaskAdmin)
admin_site.register(models.Press, PressAdmin)

# payments

admin_site.register(payment.models.Transaction, TransactionAdmin)
admin_site.register(payment.models.PaymentResponse, PaymentResponseAdmin)
admin_site.register(payment.models.Receiver, ReceiverAdmin)

# add the djcelery admin interface
# https://raw.github.com/ask/django-celery/2.4/djcelery/admin.py

admin_site.register(TaskState, TaskMonitor)
admin_site.register(WorkerState, WorkerMonitor)
admin_site.register(IntervalSchedule)
admin_site.register(CrontabSchedule)
admin_site.register(PeriodicTask, PeriodicTaskAdmin)

# add the django-notification admin panel
# https://github.com/jtauber/django-notification/blob/master/notification/admin.py

admin_site.register(NoticeQueueBatch, NoticeQueueBatchAdmin)
admin_site.register(NoticeType, NoticeTypeAdmin)
admin_site.register(NoticeSetting, NoticeSettingAdmin)
admin_site.register(Notice, NoticeAdmin)
admin_site.register(ObservedItem)
