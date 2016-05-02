"""
external library imports
"""
import pickle

"""
django imports
"""
from django import forms
from django.contrib.admin import ModelAdmin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from djcelery.admin import (
    TaskState,
    WorkerState,
    TaskMonitor,
    WorkerMonitor,
    IntervalSchedule,
    CrontabSchedule,
    PeriodicTask,
    PeriodicTaskAdmin
)
from notification.admin import NoticeTypeAdmin, NoticeSettingAdmin, NoticeAdmin
from notification.models import (
    NoticeType,
    NoticeSetting,
    Notice,
    ObservedItem,
    NoticeQueueBatch
)
from selectable.forms import AutoCompleteSelectWidget,AutoCompleteSelectField

"""
regluit imports
"""
from regluit import payment
from regluit.core import models
from regluit.marc.models import MARCRecord
from regluit.api.models import AllowedRepo
from regluit.core.lookups import (
    PublisherNameLookup,
    WorkLookup,
    OwnerLookup,
    EditionLookup
)
from regluit.libraryauth.models import Library, Block, CardPattern, EmailPattern
from regluit.libraryauth.admin import LibraryAdmin, BlockAdmin, CardPatternAdmin, EmailPatternAdmin


class RegluitAdmin(AdminSite):
    login_template = 'registration/login.html'

class UserAdmin(ModelAdmin):
    search_fields = ['username', 'email']
    list_display = ('username', 'email')

class ClaimAdminForm(forms.ModelForm):
    work = AutoCompleteSelectField(
            WorkLookup,
            widget=AutoCompleteSelectWidget(WorkLookup),
            required=True,
        )
    user = AutoCompleteSelectField(
            OwnerLookup,
            widget=AutoCompleteSelectWidget(OwnerLookup),
            required=True,
        )
    class Meta(object):
        model = models.Claim

class ClaimAdmin(ModelAdmin):
    list_display = ('work', 'rights_holder', 'status')
    date_hierarchy = 'created'
    form = ClaimAdminForm
    
class RightsHolderAdminForm(forms.ModelForm):
    owner = AutoCompleteSelectField(
            OwnerLookup,
            widget=AutoCompleteSelectWidget(OwnerLookup),
            required=True,
        )
    class Meta(object):
        model = models.RightsHolder

class RightsHolderAdmin(ModelAdmin):
    date_hierarchy = 'created'
    form = RightsHolderAdminForm

class AcqAdmin(ModelAdmin):
    readonly_fields = ('work', 'user', 'lib_acq', 'watermarked')
    search_fields = ['user__username']
    date_hierarchy = 'created'

class PremiumAdmin(ModelAdmin):
    list_display = ('campaign', 'amount', 'description')
    date_hierarchy = 'created'

class CampaignAdmin(ModelAdmin):
    list_display = ('work', 'created', 'status')
    date_hierarchy = 'created'
    exclude = ('edition', 'work', 'managers', 'publisher', 'activated', 'deadline')
    search_fields = ['work']

class WorkAdmin(ModelAdmin):
    search_fields = ['title']
    ordering = ('title',)
    list_display = ('title', 'created')
    date_hierarchy = 'created'
    fields = ('title', 'description', 'language', 'featured')

class AuthorAdmin(ModelAdmin):
    search_fields = ('name',)
    date_hierarchy = 'created'
    ordering = ('name',)
    exclude = ('editions',)

subject_authorities = (('','keywords'),('lcsh', 'LC subjects'), ('lcc', 'LC classifications'), ('bisacsh', 'BISAC heading'),  )
class SubjectAdminForm(forms.ModelForm):
    authority = forms.ChoiceField(choices=subject_authorities, required=False )
    class Meta(object):
        model = models.Subject
        fields = 'name', 'authority', 'is_visible'
    
    
class SubjectAdmin(ModelAdmin):
    search_fields = ('name',)
    date_hierarchy = 'created'
    ordering = ('name',)
    form = SubjectAdminForm
    
class EditionAdminForm(forms.ModelForm):
    work = AutoCompleteSelectField(
            WorkLookup,
            label='Work',
            widget=AutoCompleteSelectWidget(WorkLookup),
            required=True,
        )
    publisher_name = AutoCompleteSelectField(
            PublisherNameLookup,
            label='Name',
            widget=AutoCompleteSelectWidget(PublisherNameLookup),
            required=True,
        )
    class Meta(object):
        model = models.Edition
        
class EditionAdmin(ModelAdmin):
    list_display = ('title', 'publisher_name', 'created')
    date_hierarchy = 'created'
    ordering = ('title',)
    form = EditionAdminForm

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

class RelationAdmin(ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ['name']
    
class EbookAdmin(ModelAdmin):
    search_fields = ('edition__title','^url')  # search by provider using leading url
    list_display = ('__unicode__','created', 'user','edition')
    date_hierarchy = 'created'
    ordering = ('edition__title',)
    exclude = ('edition','user', 'filesize')

class WishlistAdmin(ModelAdmin):
    date_hierarchy = 'created'

class UserProfileAdmin(ModelAdmin):
    search_fields = ('user__username',)
    date_hierarchy = 'created'
    exclude = ('user',)

class GiftAdmin(ModelAdmin):
    list_display = ('to', 'acq_admin_link', 'giver', )
    search_fields = ('giver__username', 'to')
    readonly_fields = ('giver', 'acq',) 
    def acq_admin_link(self, gift):
        return "<a href='/admin/core/acq/%s/'>%s</a>" % (gift.acq.id, gift.acq)
    acq_admin_link.allow_tags = True

class CeleryTaskAdmin(ModelAdmin):
    pass

class TransactionAdmin(ModelAdmin):
    list_display = ('campaign', 'user', 'amount', 'status', 'error')
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
    
class MARCRecordAdminForm(forms.ModelForm):
    edition = AutoCompleteSelectField(
            EditionLookup,
            widget=AutoCompleteSelectWidget(EditionLookup),
            required=True,
    )
    user = AutoCompleteSelectField(
            OwnerLookup,
            widget=AutoCompleteSelectWidget(OwnerLookup),
            required=True,
        )
    class Meta(object):
        model = MARCRecord

class MARCRecordAdmin(ModelAdmin):
    list_display = ('edition', 'user')
    date_hierarchy = 'created'
    form = MARCRecordAdminForm

class AllowedRepoAdmin(ModelAdmin):
    list_display = ('org', 'repo_name')

admin_site = RegluitAdmin("Admin")

admin_site.register(User, UserAdmin)
admin_site.register(Library, LibraryAdmin)
admin_site.register(Block, BlockAdmin)
admin_site.register(CardPattern, CardPatternAdmin)
admin_site.register(EmailPattern, EmailPatternAdmin)
admin_site.register(models.Acq, AcqAdmin)
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
admin_site.register(models.Gift, GiftAdmin)
admin_site.register(MARCRecord, MARCRecordAdmin)
admin_site.register(AllowedRepo, AllowedRepoAdmin)
admin_site.register(models.Relation, RelationAdmin)

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


from regluit.questionnaire.admin import (
    Questionnaire, QuestionnaireAdmin, Question, QuestionAdmin,
    QuestionSet, QuestionSetAdmin, RunInfo, RunInfoAdmin, RunInfoHistory, RunInfoHistoryAdmin,
    Answer, AnswerAdmin, LandingAdmin, Landing,
    )
from regluit.questionnaire.admin import Subject as QSubject
from regluit.questionnaire.admin import SubjectAdmin as QSubjectAdmin

admin_site.register(Landing, LandingAdmin)

admin_site.register(Questionnaire, QuestionnaireAdmin)
admin_site.register(Question, QuestionAdmin)
admin_site.register(QuestionSet, QuestionSetAdmin)
admin_site.register(QSubject, QSubjectAdmin)
admin_site.register(RunInfo, RunInfoAdmin) 
admin_site.register(RunInfoHistory, RunInfoHistoryAdmin) 
admin_site.register(Answer, AnswerAdmin)