"""
This takes a MARCXML filename as an argument and converts it into
MARC records for the unglued edition (in .xml and .mrc formats).
Consider it a catalogolem: http://commons.wikimedia.org/wiki/File:Arcimboldo_Librarian_Stokholm.jpg
Use the MARCXML file for the non-unglued edition from Library of Congress.
"""

import pymarc
import logging
from datetime import datetime
from StringIO import StringIO

from django.conf import settings
from django.core.urlresolvers import reverse

import regluit.core.cc as cc

def stub(edition):
    
    record = pymarc.Record(force_utf8=True)

    now = datetime.now()
    
    #mostly to identify this record as a stub
    field001 = pymarc.Field(tag='001', data='stb'+now.strftime('%y%m%d%H%M%S'))
    record.add_ordered_field(field001)
    
    add_stuff(record)
    
    # fun fun fun 008
    new_field_value= now.strftime('%y%m%d')+'s'
    if edition.publication_date and len(edition.publication_date)>3:
        new_field_value += edition.publication_date[0:4]
    else:
        new_field_value += '||||'
    new_field_value += '||||xx |||||o|||||||||||eng||'
    field008 = pymarc.Field(tag='008', data=new_field_value)
    record.add_ordered_field(field008)   
        
    # add IBSN for if available
    if edition.isbn_13:
        field020 = pymarc.Field(
            tag='020',
            indicators = [' ', ' '],
            subfields = ['a', edition.isbn_13]
        )
        record.add_ordered_field(field020)
    
    # OCLC number
    if edition.oclc:
        field035 = pymarc.Field(
            tag='035',
            indicators = [' ', ' '],
            subfields = ['a', '(OCoLC)' + edition.oclc]
        )
        record.add_ordered_field(field035)
        
    # author name
    num_auths = len(edition.authnames())
    if num_auths:
        field100 = pymarc.Field(
            tag='100',
            indicators = ['1', ' '],
            subfields = [
                'a', edition.authnames()[0],
            ]
        )
        record.add_ordered_field(field100)
    if num_auths > 1:
        for auth in edition.authnames()[1:]:
            field = pymarc.Field(
                tag='700',
                indicators = ['1', ' '],
                subfields = [
                    'a', auth,
                    'e', 'joint author.',
                ]
            )
            record.add_ordered_field(field)

    # add subfield to 245 indicating format
    field245 = pymarc.Field(
        tag='245',
        indicators = ['1', '0'],
        subfields = [
            'a', edition.title,
            'a', '[electronic resource]',
        ]
    )
    record.add_ordered_field(field245)
    
    #edition statement
    if edition.note:
        field250 = pymarc.Field(
            tag='250',
            indicators = [' ', ' '],
            subfields = [
                'a', unicode(edition.note),
            ]
        )
        record.add_ordered_field(field250)
    
    # publisher, date
    if edition.publisher:
        field260 = pymarc.Field(
            tag='260',
            indicators = [' ', ' '],
            subfields = [
                'b', edition.publisher,
            ]
        )
        if edition.publication_date:
            field260.add_subfield('c', unicode(edition.publication_date))
        record.add_ordered_field(field260)
    
    if edition.description:
        #add 520 field (description)
        field520 =  pymarc.Field(
            tag='520',
            indicators = [' ', ' '],
            subfields = [
                'a', edition.description,
            ]
        )
        record.add_ordered_field(field520)
        
    add_license(record, edition)
    
    return record

#load a with minimal change
def raw(marcfile,  edition):
    record = pymarc.parse_xml_to_array(marcfile)[0]
    for field in record:
        if field.tag in ('001', '003', '005', '006', '007', '856') or int( field.tag ) > 900:
            record.remove_field(field)
    add_stuff(record)
    return record
    
#load a record from library of Congress
def from_lc(marcfile,  edition):
    
    # save lccn for later (if there is one) before deleting it
    print_lccn = None
    record = pymarc.parse_xml_to_array(marcfile)[0]
    for lccn in record.get_fields('010'):
        for validlccn in lccn.get_subfields('a'):
            print_lccn = validlccn
    for field in record:
        if field.tag in ('001', '003', '005', '006', '007', '010', '040', '856') or int( field.tag ) > 900:
            record.remove_field(field)

    add_stuff(record)
    
    field008 = record.get_fields('008')[0]
    record.remove_field(field008)
    old_field_value = field008.value()
    new_field_value = old_field_value[:23] + 'o' + old_field_value[24:]
    field008 = pymarc.Field(tag='008', data=new_field_value)
    record.add_ordered_field(field008)   
        
    # add IBSN for ebook where applicable; relegate print ISBN to $z
    isbn = edition.isbn_13
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
    try:
        field245 = record.get_fields('245')[0]
        field245.add_subfield('a', '[electronic resource]')
    except IndexError:
        pass
        
    # modify 300 field (physical description)
    try:
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
    except:
        pass
    
    add_license(record, edition)

    # add 588 field (source of description) - credit where credit is due
    if print_lccn:
        field588 = pymarc.Field(
            tag='588',
            indicators = [' ', ' '],
            subfields = [
                'a', 'Description based on print version record from the Library of Congress.',
            ]
        )
        record.add_ordered_field(field588)
    
    # add 776 field (related editions) - preserve pISBN, LCCN, OCLCnum
    title = record.get_fields('245')[0].get_subfields('a')[0]
    title = title.split('/')[0]
    
    subfields = ['i', 'Print version: ','t', title,]
    
    if print_isbn:
        subfields.extend(['z', print_isbn])
    elif isbn:
        subfields.extend(['z', isbn])
    if print_lccn:
        subfields.extend(['w', '(DLC) ' + print_lccn, ])
    if edition.oclc:
        subfields.extend(['w', '(OCoLC) ' + edition.oclc,])

    field776 = pymarc.Field(
        tag='776',
        indicators = ['0', '8'],
        subfields = subfields
    )
    
    record.add_ordered_field(field776)
        
    return record

def add_license(record, edition):
    if edition.license:
        # add 536 field (funding information)
        field536 = pymarc.Field(
            tag='536',
            indicators = [' ', ' '],
            subfields = [
                'a', edition.funding_info,
            ]
        )
        record.add_ordered_field(field536)
    
        # add 540 field (terms governing use)
        field540 = pymarc.Field(
            tag='540',
            indicators = [' ', ' '],
            subfields = [
                'a', dict(cc.CHOICES)[edition.license],
                'u', dict(cc.GRANTS)[edition.license], 
            ]
        )
        record.add_ordered_field(field540)

def add_stuff(record):
    # add field indicating record originator
    field003 = pymarc.Field(tag='003', data='UnglueIt')
    record.add_ordered_field(field003)
    
    # update timestamp of record
    datestamp = datetime.now().strftime('%Y%m%d%H%M%S') + '.0'
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
