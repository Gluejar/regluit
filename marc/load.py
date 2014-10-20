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
from regluit.core import models

def stub(edition):
    
    record = pymarc.Record()

    now = datetime.now()
    
    #mostly to identify this record as a stub
    field001 = pymarc.Field(tag='001', data='stb'+now.strftime('%y%m%d%H%M%S'))
    record.add_ordered_field(field001)
        
    # add field indicating record originator
    field003 = pymarc.Field(tag='003', data='UnglueIt')
    record.add_ordered_field(field003)
    
    # update timestamp of record
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
    
    return record
