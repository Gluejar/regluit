import pymarc
import logging
from datetime import datetime
from StringIO import StringIO

from django.conf import settings
from django.db import models

# weak coupling
EDITION_MODEL = "core.Edition"

class Edition:
    # define the methods an edition should have
    
    # the edition should be able to report ebook downloads, with should have format and url attributes
    def downloads(self):
        return []

    # the edition should be able to report "ebook via" url
    def download_via_url(self):
        return []

def _xml(record):
    return pymarc.record_to_xml(record)

def _mrc(record):
    mrc_file = StringIO()
    writer = pymarc.MARCWriter(mrc_file)
    writer.write(record)
    mrc_file.seek(0)
    return mrc_file.read()

class MARCRecord(models.Model):
    # the record  goes here
    guts = models.TextField()
    
    # note capitalization of related_name
    edition = models.ForeignKey(EDITION_MODEL, related_name="MARCRecords", null=True)
    
    @property
    def accession(self):
        zeroes = 9 - len(str(self.id))
        return 'ung' + zeroes*'0' + str(self.id)
       
    # the record without 856 
    def _record(self):
        the_record = pymarc.parse_xml_to_array(StringIO(self.guts))[0]
        fields856 = the_record.get_fields('856')
        if fields856:
            the_record.remove_field(fields856)
        return the_record
        
    def direct_record(self):
        the_record = self._record()
        for book in self.edition.downloads():
            field856 = pymarc.Field(
                tag='856',
                indicators = ['4', '0'],
                subfields = [
                    '3', book.format + ' version',
                    'q', settings.CONTENT_TYPES[book.format],
                    'u', book.url,
                ]
            )
            the_record.add_ordered_field(field856)
        return the_record

    def direct_record_xml(self):
        return _xml(self.direct_record())

    def direct_record_mrc(self):
        return _mrc(self.direct_record())

    def via_record(self):
        the_record = self._record()
        field856_via = pymarc.Field(
            tag='856',
            indicators = ['4', '0'],
            subfields = [
                'u', self.edition.download_via_url(),
            ]
        )
        the_record.add_ordered_field(field856_via)
        return the_record

    def via_record_xml(self):
        return _xml(self.via_record())

    def via_record_mrc(self):
        return _mrc(self.via_record())

