"""
This takes a MARCXML filename as an argument and converts it into
MARC records for the unglued edition (in .xml and .mrc formats).
Use the MARCXML file for the non-unglued edition from Library of Congress.
"""

import logging
import sys
import pymarc
from datetime import datetime
from StringIO import StringIO

from django.core.files.storage import default_storage

from regluit.core import models

def makemarc(marcfile, isbn, license, ebooks):
    """
    if we're going to suck down LOC records:
        parse_xml_to_array takes a file, so we need to faff about with file writes
        would be nice to have a suitable z39.50
        can use LCCN to grab record with urllib, but file writes are inconsistent
    """
    logger = logging.getLogger(__name__)
    record = pymarc.parse_xml_to_array(marcfile)[0]
    
    fields_to_delete = []
    fields_to_delete += record.get_fields('001')
    fields_to_delete += record.get_fields('003')
    fields_to_delete += record.get_fields('005')
    fields_to_delete += record.get_fields('006')
    fields_to_delete += record.get_fields('007')
    fields_to_delete += record.get_fields('040')
    for field in fields_to_delete:
        record.remove_field(field)
        
    # create accession number and write 001 field 
    # (control field syntax is special)
    marc_record = models.MARCRecord()
    marc_record.save()
    marc_id = marc_record.id
    zeroes = 9 - len(str(marc_record.id))
    accession = 'ung' + zeroes*'0' + str(marc_id)
    field001 = pymarc.Field(tag='001', data=accession)
    record.add_ordered_field(field001)

    # add field indicating record originator
    field003 = pymarc.Field(tag='003', data='UnglueIt')
    record.add_ordered_field(field003)
    
    # update timestamp of record
    now = datetime.now()
    datestamp = now.strftime('%Y%m%d%H%M%S') + '.0'
    field005 = pymarc.Field(tag='005', data=datestamp)
    record.add_ordered_field(field005)

    # change 006, 007, 008 because this is an online resource
    field006 = pymarc.Field(
        tag='006',
        data='m     o  d        '
    )
    record.add_ordered_field(field006)

    field007 = pymarc.Field(
        tag='007',
        data='cr'
    )
    record.add_ordered_field(field007)
    
    field008 = record.get_fields('008')[0]
    record.remove_field(field008)
    old_field_value = field008.value()
    new_field_value = old_field_value[:23] + 'o' + old_field_value[24:]
    field008 = pymarc.Field(tag='008', data=new_field_value)
    record.add_ordered_field(field008)
    
    # add subfield to 245 indicating format
    field245 = record.get_fields('245')[0]
    field245.add_subfield('h', '[electronic resource]')

    # modify 300 field (physical description)
    field300 = record.get_fields('300')[0]
    subfield_a = field300.get_subfields('a')[0]
    if (
        subfield_a[-2:] == ' ;' or 
        subfield_a[-2:] == ' :' or 
        subfield_a[-2:] == ' +'
    ):
        subfield_a = subfield_a[:-2]
    new300a = 'online resource (' + subfield_a + ')'
    if field300.get_subfields('b'):
        new300a += ' :'
    field300.delete_subfield('a')
    field300.add_subfield('a', new300a)
    field300.delete_subfield('c')

    # add 536 field (funding information)
    field536 = pymarc.Field(
        tag='536',
        indicators = [' ', ' '],
        subfields = [
            'a', 'The book is available as a free download thanks to the generous support of interested readers and organizations, who made donations using the crowd-funding website Unglue.it.',
        ]
    )
    record.add_ordered_field(field536)
    
    # add 540 field (terms governing use)
    license_terms = {
        'BY': 'Creative Commons Attribution 3.0 Unported (CC BY 3.0)',
        'BY-SA': 'Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY 3.0)',
        'BY-NC': 'Creative Commons Attribution-NonCommercial 3.0 Unported (CC BY 3.0)',
        'BY-NC-SA': 'Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported (CC BY 3.0)',
        'BY-NC-ND': 'Creative Commons Attribution-NonCommercial-NoDerivs 3.0 Unported (CC BY 3.0)',
        'BY-ND': 'Creative Commons Attribution-NoDerivs 3.0 Unported (CC BY 3.0)',
    }
    license_grants = {
        'BY': 'http://creativecommons.org/licenses/by/3.0/',
        'BY-SA': 'http://creativecommons.org/licenses/by-sa/3.0/',
        'BY-NC': 'http://creativecommons.org/licenses/by-nc/3.0/',
        'BY-NC-SA': 'http://creativecommons.org/licenses/by-nc-sa/3.0/',
        'BY-NC-ND': 'http://creativecommons.org/licenses/by-nc-nd/3.0/',
        'BY-ND': 'http://creativecommons.org/licenses/by-nd/3.0/'        
    }
    field540 = pymarc.Field(
        tag='540',
        indicators = [' ', ' '],
        subfields = [
            'a', license_terms[license],
            'u', license_grants[license],
        ]
    )
    record.add_ordered_field(field540)

    # add 588 field (source of description) - credit where credit is due
    field588 = pymarc.Field(
        tag='588',
        indicators = [' ', ' '],
        subfields = [
            'a', 'Description based on print version record from the Library of Congress.',
        ]
    )
    record.add_ordered_field(field588)

    # add 856 fields with links for each available file
    content_types = {
        'PDF': 'application/pdf',
        'EPUB': 'application/epub+zip',
        'HTML': 'text/html',
        'TEXT': 'text/plain',
        'MOBI': 'application/x-mobipocket-ebook'
    }
    for format in ebooks:
        if ebooks[format]:            
            field856 = pymarc.Field(
                tag='856',
                indicators = ['4', '0'],
                subfields = [
                    '3', format + ' version',
                    'q', content_types[format.upper()],
                    'u', ebooks[format],
                ]
            )
            record.add_ordered_field(field856)

    # strip any 9XX fields (they're for local use)    
    for i in range(900, 1000):
        fields = record.get_fields(str(i))
        for field in fields:
            record.remove_field(field)
    
    # write the unglued MARCxml records
    xml_filename = 'marc/' + isbn + '_unglued.xml'
    xmlrecord = pymarc.record_to_xml(record)
    xml_file = default_storage.open(xml_filename, 'rw')
    xml_file.write(xmlrecord)
    
    # write the unglued .mrc record, then save to s3
    string = StringIO()
    mrc_filename = 'marc/' + isbn + '_unglued.mrc'
    writer = pymarc.MARCWriter(string)
    writer.write(record)
    mrc_file = default_storage.open(mrc_filename, 'rw')
    mrc_file.write(string.getvalue())
    
    # add the records we just created to our active MARCRecord instance
    marc_record.xml_record = xml_file
    marc_record.mrc_record = mrc_file
    xml_file.close()
    mrc_file.close()
    marc_record.save()
