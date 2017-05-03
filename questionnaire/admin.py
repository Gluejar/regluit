from django.utils.translation import ugettext as _
from django.contrib import admin
from django.core.urlresolvers import reverse
from .models import (Choice, Questionnaire, Question, QuestionSet, Subject, 
        RunInfo, RunInfoHistory, Answer, DBStylesheet, Landing)

adminsite = admin.site


class SubjectAdmin(admin.ModelAdmin):
    search_fields = ['surname', 'givenname', 'email']
    list_display = ['surname', 'givenname', 'email']


class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['sortid', 'text', 'value', 'question']


class ChoiceInline(admin.TabularInline):
    ordering = ['sortid']
    model = Choice
    extra = 5


class QuestionSetAdmin(admin.ModelAdmin):
    ordering = ['questionnaire', 'sortid', ]
    list_filter = ['questionnaire', ]
    list_display = ['questionnaire', 'heading', 'sortid', ]
    list_editable = ['sortid', ]


class QuestionAdmin(admin.ModelAdmin):
    ordering = ['questionset__questionnaire', 'questionset', 'sort_id', 'number']
    inlines = [ChoiceInline]
    list_filter = ['questionset__questionnaire']

    def changelist_view(self, request, extra_context=None):
        "Hack to have Questionnaire list accessible for custom changelist template"
        if not extra_context:
            extra_context = {}

        questionnaire_id = request.GET.get('questionset__questionnaire__id__exact', None)
        if questionnaire_id:
            args = {"id": questionnaire_id}
        else:
            args = {}
        extra_context['questionnaires'] = Questionnaire.objects.filter(**args).order_by('name')
        return super(QuestionAdmin, self).changelist_view(request, extra_context)


class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ('name', 'redirect_url', 'export')
    readonly_fields = ('export',)

    def export(self, obj):
        csv_url = reverse("export_csv", args=[obj.id,])
        summary_url = reverse("export_summary", args=[obj.id,])
        return '<a href="{}">{}</a> <a href="{}">{}</a>'.format(
            csv_url, _("Download data"), summary_url, _("Show summary")
        )

    export.allow_tags = True
    export.short_description = _('Export to CSV')


class RunInfoAdmin(admin.ModelAdmin):
    list_display = ['random', 'run', 'subject', 'created', 'emailsent', 'lastemailerror']
    pass


class RunInfoHistoryAdmin(admin.ModelAdmin):
    pass


class AnswerAdmin(admin.ModelAdmin):
    search_fields = ['subject__email', 'run__id', 'question__number', 'answer']
    list_display = ['id', 'run', 'subject', 'question']
    list_filter = ['subject', 'run__id']
    ordering = [ 'id', 'subject', 'run__id', 'question', ]
    
from django.contrib import admin

# new in dj1.7
# @admin.register(Landing)
class LandingAdmin(admin.ModelAdmin):
    list_display = ('label', 'content_type', 'object_id', )
    ordering = [ 'object_id', ]

adminsite.register(Questionnaire, QuestionnaireAdmin)
adminsite.register(Question, QuestionAdmin)
adminsite.register(QuestionSet, QuestionSetAdmin)
adminsite.register(Subject, SubjectAdmin)
adminsite.register(RunInfo, RunInfoAdmin) 
adminsite.register(RunInfoHistory, RunInfoHistoryAdmin) 
adminsite.register(Answer, AnswerAdmin)
adminsite.register(Landing, LandingAdmin)
adminsite.register(DBStylesheet)
