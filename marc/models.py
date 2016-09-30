import pymarc
import logging
from datetime import datetime
from StringIO import StringIO

from django.apps import apps
from django.conf import settings
from django.db import models

from . import load

# weak coupling
EDITION_MODEL = getattr(settings, "EDITION_MODEL", "core.Edition")

logger = logging.getLogger(__name__)

marc_rels = {
    'aut': 'author',
    "adp": "adapter",
    "aft": "author_of_afterword",
    "ann": "annotator",
    "arr": "arranger",
    "art": "artist",
    "aui": "author_of_introduction",
    "clb": "collaborator",
    "cmm": "commentator",
    "cmp": "composer",
    "cnd": "conductor",
    "com": "compiler",
    "ctb": "contributor",
    "dsr": "designer",
    "dub": "dubious_author",
    "edt": "editor",
    "egr": "engineer",
    "ill": "illustrator",
    "lbt": "librettist",
    "oth": "other_contributor",
    "pbl": "publisher_contributor",
    "pht": "photographer",
    "prf": "performer",
    "prt": "printer",
    "res": "researcher", 
    "trc": "transcriber",
    "trl": "translator",
    "unk": "unknown_contributor",
    }
inverse_marc_rels = {v:k for k,v in  marc_rels.items()}

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
    note = ''
    
    # the edition should be able to report ebook downloads, with should have format and url attributes
    def downloads(self):
        return []

    # the edition should be able to report an "ebook via" url
    def download_via_url(self):
        return []

    # these should be last name first
    def authnames(self):
        return []
    
    # gets the right edition
    @staticmethod   
    def get_by_isbn(isbn):
        return None
                
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
    
    user =  models.ForeignKey(settings.AUTH_USER_MODEL, related_name="MARCRecords", null=True ) 
    created =  models.DateTimeField(auto_now_add=True)  


    def __init__(self, *args,  **kwargs):
        _the_record = kwargs.pop('the_record', None)
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
            self.guts = ''
            super(MARCRecord, self).save(*args, **kwargs) 
            self.guts = _xml(self._the_record)
            try:
                field001 = self._the_record.get_fields('001')[0]
                if field001:
                    self._the_record.remove_field(field001)
            except IndexError:
                pass
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

#load a many records minimal change
def import_records(marcfile):

    class RecordLoader(pymarc.XmlHandler):
        Edition = apps.get_model(*EDITION_MODEL.split('.'))
        num_loaded=0
        def process_record(self, record):
            try:
                field020 = record.get_fields('020')[0]
                isbn =  field020.get_subfields('a')[0]
                edition = self.Edition.get_by_isbn(isbn)
                if edition:
                    try:
                        mr = MARCRecord.objects.get(edition=edition)
                        logger.info('already have a record for %s' % isbn)
                    except MARCRecord.DoesNotExist:
                        mr = MARCRecord(edition=edition, the_record=record)
                        mr.save()
                        self.num_loaded+=1
                else:
                    logger.info('no edition for %s' % isbn)
            except IndexError:
                logger.info('020 absent')
     
    handler = RecordLoader()
    pymarc.parse_xml(marcfile, handler) 
    return handler.num_loaded
