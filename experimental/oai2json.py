#!/usr/bin/env python

import re
import sys
import json
import urllib

import requests
from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, oai_dc_reader

def lookup(oai_url, set_name):
    registry = MetadataRegistry()
    registry.registerReader('oai_dc', oai_dc_reader)
    client = Client(oai_url, registry)
    for header, record, other in client.listRecords(metadataPrefix='oai_dc', set=set_name):
        if not record:
            continue
        title = record.getField('title')[0]
        authors = record.getField('creator')
        urls = record.getField('identifier')
        subjects = record.getField('subject')
        id = header.identifier()
        record = {
            "id": id,
            "title": title,
            "authors": authors,
            "subjects": subjects,
            "urls": urls,
        }
        print json.dumps(record)

if __name__ == "__main__":
    oai_url = sys.argv[1]
    set_name = None
    if len(sys.argv) > 2:
        set_name = sys.argv[2]
    lookup(oai_url, set_name)
