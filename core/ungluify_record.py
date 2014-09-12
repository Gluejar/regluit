"""
This takes a MARCXML filename as an argument and converts it into
MARC records for the unglued edition (in .xml and .mrc formats).
Consider it a catalogolem: http://commons.wikimedia.org/wiki/File:Arcimboldo_Librarian_Stokholm.jpg
Use the MARCXML file for the non-unglued edition from Library of Congress.
"""

import logging
import pymarc
from copy import deepcopy
from datetime import datetime
from StringIO import StringIO

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse

import regluit.core.cc as cc
from regluit.core import models

def makemarc(marcfile,  edition):
    logger = logging.getLogger(__name__)
    
    try:
        license = edition.ebooks.all()[0].rights
        ebf = None
    except IndexError:
        license = None
        ebf = edition.ebook_files.all()[0]
    
    logger.info("Making MARC records for edition %s " % edition)
        
    record = pymarc.parse_xml_to_array(marcfile)[0]
    
    # save lccn for later (if there is one) before deleting it
    print_lccn = None
    for lccn in record.get_fields('010'):
        for validlccn in lccn.get_subfields('a'):
            print_lccn = validlccn

    fields_to_delete = []
    fields_to_delete += record.get_fields('001')
    fields_to_delete += record.get_fields('003')
    fields_to_delete += record.get_fields('005')
    fields_to_delete += record.get_fields('006')
    fields_to_delete += record.get_fields('007')
    fields_to_delete += record.get_fields('010')
    fields_to_delete += record.get_fields('040')
    for field in fields_to_delete:
        record.remove_field(field)
        
    # create accession number and write 001 field 
    # (control field syntax is special)
    if ebf:
        (marc_record, created) = models.MARCRecord.objects.get_or_create(edition=edition,link_target='B2U')
    else:
        (marc_record, created) = models.MARCRecord.objects.get_or_create(edition=edition,link_target='UNGLUE')
    field001 = pymarc.Field(tag='001', data=marc_record.accession)
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
    
    # add IBSN for ebook where applicable; relegate print ISBN to $z
    isbn = ''
    try:
        isbn = edition.identifiers.filter(type='isbn')[0].value
    except IndexError:
        pass
    try:
        field020 = record.get_fields('020')[0]
        print_isbn = field020.get_subfields('a')[0]
        field020.delete_subfield('a')
        if isbn:
            field020.add_subfield('a', isbn)
        field020.add_subfield('z', print_isbn)
    except IndexError:
        print_isbn = None

    # change 050 and 082 indicators because LOC is no longer responsible for these
    # no easy indicator change function, so we'll just reconstruct the fields
    try:
        field050 = record.get_fields('050')[0]
        field050_new = field050
        field050_new.indicators = [' ', '4']
        record.remove_field(field050)
        record.add_ordered_field(field050_new)
    except:
        pass # if no 050 field, don't need to change indicator
    
    try:
        field082 = record.get_fields('082')[0]
        field082_new = field082
        field082_new.indicators = [' ', '4']
        record.remove_field(field082)
        record.add_ordered_field(field082_new)
    except:
        pass # if no 082 field, don't need to change indicator

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
    new300a = '1 online resource (' + subfield_a + ')'
    if field300.get_subfields('b'):
        new300a += ' :'
    field300.delete_subfield('a')
    field300.add_subfield('a', new300a)
    field300.delete_subfield('c')
    
    if license:
        # add 536 field (funding information)
        if edition.unglued:
            funding_info = 'The book is available as a free download thanks to the generous support of interested readers and organizations, who made donations using the crowd-funding website Unglue.it.'
        else:
            if edition.ebooks.all()[0].rights in cc.LICENSE_LIST:
                funding_info = 'The book is available as a free download thanks to a Creative Commons license.'
            else:
                funding_info = 'The book is available as a free download because it is in the Public Domain.'
        field536 = pymarc.Field(
            tag='536',
            indicators = [' ', ' '],
            subfields = [
                'a', funding_info,
            ]
        )
        record.add_ordered_field(field536)
    
        # add 540 field (terms governing use)
        field540 = pymarc.Field(
            tag='540',
            indicators = [' ', ' '],
            subfields = [
                'a', dict(cc.CHOICES)[license],
                'u', dict(cc.GRANTS)[license], 
            ]
        )
        record.add_ordered_field(field540)

    # add 588 field (source of description) - credit where credit is due
    field588 = pymarc.Field(
        tag='588',
        indicators = [' ', ' '],
        if print_lccn:
            subfields = [
                'a', 'Description based on print version record from the Library of Congress.',
            ]
    )
    record.add_ordered_field(field588)
    
    # add 776 field (related editions) - preserve pISBN, LCCN, OCLCnum
    title = record.get_fields('245')[0].get_subfields('a')[0]
    title = title.split('/')[0]
    try:
        oclcnum = edition.identifiers.filter(type='oclc')[0].value
    except IndexError:
        oclcnum = None
    
    subfields = ['i', 'Print version: ','t', title,]
    
    if print_isbn:
        subfields.extend(['z', print_isbn])
    if print_lccn:
        subfields.extend(['w', '(DLC) ' + print_lccn, ])
    if oclcnum:
        subfields.extend(['w', '(OCoLC) ' + oclcnum,])

    field776 = pymarc.Field(
        tag='776',
        indicators = ['0', '8'],
        subfields = subfields
    )
    
    record.add_ordered_field(field776)
    """
    add 776 fields
    indicators: 0 8
    '$i Print version: '
    $t Title. <--note space
    $d is optional
    $z pISBN goes here
        harvest from 020 (was moved from $a to $z)
    $w (DLC) LCCN_goes_here
        harvest from 010 field before deletion
    $w (OCoLC) OCLCnum_goes_here
        harvest from identifiers db
    """

    # strip any 9XX fields (they're for local use)    
    for i in range(900, 1000):
        fields = record.get_fields(str(i))
        for field in fields:
            record.remove_field(field)
    
    # add 856 fields with links for each available file
    # doing this out of order as it's the only thing that differs
    # between direct-link and via-unglue.it versions
    if not ebf:
        # need deepcopy() because omg referential transparency!
        record_direct = deepcopy(record)  # 2 records for unglued stuff
    
        for format_tuple in settings.FORMATS:
            format = format_tuple[0]
            ebooks = edition.ebooks.filter(format=format)
            if ebooks:
                for book in ebooks:
                    field856 = pymarc.Field(
                        tag='856',
                        indicators = ['4', '0'],
                        subfields = [
                            '3', format + ' version',
                            'q', settings.CONTENT_TYPES[format],
                            'u', book.url,
                        ]
                    )
                    record_direct.add_ordered_field(field856)
                
    unglued_url = settings.BASE_URL_SECURE + reverse('download', args=[edition.work.id])
    field856_via = pymarc.Field(
        tag='856',
        indicators = ['4', '0'],
        subfields = [
            'u', unglued_url,
        ]
    )
    record.add_ordered_field(field856_via)

    if not ebf:
        # this via_unglueit record needs its own accession number
        field001 = record_direct.get_fields('001')[0]
        record_direct.remove_field(field001)
        (marc_record_direct, created) = models.MARCRecord.objects.get_or_create(edition=edition,link_target='DIRECT')
        field001 = pymarc.Field(tag='001', data=marc_record_direct.accession)
        record_direct.add_ordered_field(field001)

        # write the unglued MARCxml records
        xmlrecord = pymarc.record_to_xml(record_direct)
        xml_file = default_storage.open(marc_record_direct.xml_record, 'w')
        xml_file.write(xmlrecord)
        xml_file.close()
    
        # write the unglued .mrc records, then save to s3
        mrc_file = default_storage.open(marc_record_direct.mrc_record, 'w')
        writer = pymarc.MARCWriter(mrc_file)
        writer.write(record_direct)
        mrc_file.close()

    xmlrecord = pymarc.record_to_xml(record)
    xml_file = default_storage.open(marc_record.xml_record, 'w')
    xml_file.write(xmlrecord)
    xml_file.close()

    mrc_file = default_storage.open(marc_record.mrc_record, 'w')
    writer = pymarc.MARCWriter(mrc_file)
    writer.write(record)
    mrc_file.close()

