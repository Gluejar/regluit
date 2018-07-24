from datetime import datetime
from xml.sax import SAXParseException

from django.apps import apps
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.views.generic.edit import FormView

from . import models
from . import forms

PREAMBLE = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                 '<collection '
                 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                 'xmlns="http://www.loc.gov/MARC21/slim" '
                 'xsi:schemaLocation="http://www.loc.gov/MARC21/slim '
                 'http://www.loc.gov/standards/marcxml/schema/'
                 'MARC21slim.xsd">')

Edition = apps.get_model(*models.EDITION_MODEL.split('.'))


def marc_records(request, selected_records=None):
    # TODO convert to streaming when we move to Django 1.5+
    if request.method == 'POST':
        params=request.POST
    elif request.method == 'GET':
        params=request.GET
    else:
        return HttpResponseNotFound
    format = params.get('format', 'xml')
    link_target = params.get('link_target', 'via')
    
    if selected_records==None:
        # extract the user-selected records from the params QueryDict
        selected_records = list(
            k for k in params if params[k] == u'on'
        )
    if not selected_records:
        messages.error(
            request,
            "There were no records to download."
        )
        return HttpResponseRedirect(reverse('marc', args=[]))
    
    outfile = HttpResponse('', content_type='application/marc')
    outfile['Content-Disposition'] = 'attachment; filename='+ datetime.now().strftime('%Y%m%d%H%M%S') + '.' +  format

    if format == 'xml':
        outfile.write(PREAMBLE)

    for record_name in selected_records:
        if isinstance(record_name, models.MARCRecord):
            record = record_name
        elif isinstance(record_name, Edition):
            record = models.MARCRecord(edition=record_name)
        elif hasattr(record_name, 'edition'):
            record = models.MARCRecord(edition=record_name.edition)
        elif record_name.startswith('edition_'):
            record_id = long(record_name[8:])
            try:
                edition = Edition.objects.get(pk=record_id)
            except Edition.DoesNotExist:
                continue
            record = models.MARCRecord(edition=edition)
        elif record_name.startswith('record_'):
            record_id = long(record_name[7:])
            try:
                record = models.MARCRecord.objects.get(id=record_id )
            except models.MARCRecord.DoesNotExist:
                continue
        
        outfile.write(record.record(format=format, link_target=link_target))

    if format == 'xml':
        outfile.write('</collection>')

    return outfile

def all_marc_records(request):
    selected_records = list(
        'record_'+ str(record.pk) for record in models.MARCRecord.objects.all()
    )
    return marc_records(request, selected_records=selected_records)

def qs_marc_records(request, qs):
    # translate a queryset into a record list.
    selected_records = []
    for obj in qs:
        # each object must have a marc_records() attribute which returns a record list. 
        # records can be strings: 'record_xxx', 'edition_xxx', MARCRecord objs or objs with edition attributes
        selected_records.extend(obj.marc_records())
    return marc_records(request, selected_records=selected_records)

class MARCUpload(FormView):
    template_name = 'marc/upload.html'
    form_class = forms.MARCUploadForm
    success_url = reverse_lazy('upload_marc')
    
    # allow a get param to specify the edition
    def get_initial(self):
        if self.request.method == 'GET':
            edition = self.request.GET.get('edition',None)
            if Edition.objects.filter(id=edition).count():
                edition = Edition.objects.filter(id=edition)[0]
                if edition.ebooks.count() or edition.ebook_files.count():
                    return {'edition':edition.id}
        return {}

    def form_valid(self, form):
        edition = form.cleaned_data['edition']
        source = form.cleaned_data['source']
        try:
            marcfile=self.request.FILES['file']
            new_record = models.MARCRecord(
                guts=marcfile,
                edition=edition,
                user= self.request.user
            )
            new_record.load_from_file(source)
            messages.success(
                self.request,
                "You have successfully added a MARC record. Hooray! Add another?"
            )
        except SAXParseException:
            messages.error(
                self.request,
                "Sorry, couldn't parse that file."
            )
        return super(MARCUpload,self).form_valid(form)
        