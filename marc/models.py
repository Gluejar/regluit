import pymarc
import logging
from datetime import datetime
from StringIO import StringIO

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from . import load

# weak coupling
EDITION_MODEL = "core.Edition"

class AbstractEdition:
    # define the methods and attributes an edition should have
    isbn_13 = ''
    oclc = ''
    license = None
    funding_info = ''
    description = ''
    publisher = ''
    title = ''
    publication_date = ''
    
    # the edition should be able to report ebook downloads, with should have format and url attributes
    def downloads(self):
        return []

    # the edition should be able to report an "ebook via" url
    def download_via_url(self):
        return []

    # these should be last name first
    def authnames(self):
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
    
    #storage for parsed guts
    _the_record = None
    
    # note capitalization of related_name
    edition = models.ForeignKey(EDITION_MODEL, related_name="MARCRecords", null=True)
    
    user =  models.ForeignKey(User, related_name="MARCRecords", null=True ) 
    created =  models.DateTimeField(auto_now_add=True)  


    def __init__(self, *args,  **kwargs):
        super(MARCRecord, self).__init__( *args, **kwargs)
        edition = kwargs.pop('edition', None)
        guts = kwargs.pop('guts', None)
        if edition and not guts:
            #make a stub _the_record from the edition
            self._the_record = load.stub(edition)

    @property
    def accession(self):
        zeroes = 9 - len(str(self.id))
        return 'ung' + zeroes*'0' + str(self.id)
    
    def save(self, *args, **kwargs):
        if self.id == None and self._the_record:
            # get the id first, add assession number
            stash_guts = self.guts
            self.guts = ''
            super(MARCRecord, self).save(*args, **kwargs) 
            self.guts = stash_guts
            field001 = self._the_record.get_fields('001')
            if field001:
                self._the_record.remove_field(field)
            field001 = pymarc.Field(tag='001', data=self.accession)
            self._the_record.add_ordered_field(field001)
        super(MARCRecord, self).save(*args, **kwargs)
    
    def load_from_file(self, source='raw'):
        #parse guts
        if isinstance(self.guts, str) or isinstance(self.guts, unicode):
            marcfile = StringIO(self.guts)
        else:
            marcfile = self.guts
        if source == 'loc':
            self._the_record = load.from_lc(marcfile, self.edition)
        else:
            self._the_record = load.raw(marcfile, self.edition)
        self.guts = pymarc.record_to_xml(self._the_record)
        self.save()

        
    # the record without 856 
    def _record(self):
        if self._the_record:
            the_record = self._the_record
        else:
            the_record = pymarc.parse_xml_to_array(StringIO(self.guts))[0]
        for field in the_record.get_fields('856'):
            the_record.remove_field(field)
        self._the_record = the_record
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
    
    def record(self, link_target='via', format='xml'):
        if format == 'xml':
            if link_target == 'via':
                return self.via_record_xml()
            elif link_target == 'direct':
                return self.direct_record_xml()
        elif  format == 'mrc':
            if link_target == 'via':
                return self.via_record_mrc()
            elif link_target == 'direct':
                return self.direct_record_mrc()
