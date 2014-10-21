from datetime import datetime
from django.core.urlresolvers import reverse
from django.db.models import get_model
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound

from . import models

PREAMBLE = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                 '<collection '
                 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                 'xmlns="http://www.loc.gov/MARC21/slim" '
                 'xsi:schemaLocation="http://www.loc.gov/MARC21/slim '
                 'http://www.loc.gov/standards/marcxml/schema/'
                 'MARC21slim.xsd">')

Edition = get_model(*models.EDITION_MODEL.split('.'))


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
        if record_name.startswith('edition_'):
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
