"""
Utilities for calling mobigen for management. do not use in application

"""

from itertools import islice
from StringIO import StringIO
import uuid

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile, File

from regluit.core.models import (Campaign, Ebook)
from regluit.core import parameters
from regluit.core.mobi import convert_to_mobi


# compute whether we can apply mobigen to a given edition to produce a mobi file
# need to have an ebook in epub or pdf format 
# possible return values:  already has a mobi file / can generate a mobi file / not possible

def edition_mobi_status(edition):
    """
    for a given edition, return:
      * 1 if there is already a mobi ebook
      * 0 if there is none but we have an epub or html to convert from
      * -1 for no epub/html to convert from
    """
    formats = set([ebook.format for ebook in edition.work.ebooks()])
    if 'mobi' in formats:
        return 1
    elif ('epub' in formats) or ('html' in formats):
        return 0
    else:
        return -1
    

def write_file_to_storage(file_object, content_type, path):
    """
    write file_object to the default_storage at given path
    """
    file_s3 = ContentFile(file_object)
    file_s3.content_type = content_type
    
    default_storage.save(path, file_s3)
    return file_s3


# generator for editions to add mobi to
# campaigns that can have mobi files but don't yet.

def editions_to_convert():
    for campaign in Campaign.objects.filter(edition__ebooks__isnull=False).distinct():
        # need to make sure campaign type is not B2U because kindlegen is for books we give awy free of charge
        if (edition_mobi_status(campaign.edition) == 0) and (campaign.type != parameters.BUY2UNGLUE): # possible to generate mobi
            yield campaign.edition
            

def generate_mobi_ebook_for_edition(edition):
    
    # pull out the sister edition to convert from
    sister_ebook = edition.ebooks.filter(format__in=['epub', 'html'])[0]
    
    # run the conversion process

    output = convert_to_mobi(sister_ebook.url)
    #output = open("/Users/raymondyee/Downloads/hello.mobi").read()
    
    file_ = write_file_to_storage(output, 
                              "application/x-mobipocket-ebook", 
                              "/ebf/{0}.mobi".format(uuid.uuid4().get_hex()))
    
    # create a path for the ebookfile:   IS THIS NECESSARY?
    # https://github.com/Gluejar/regluit/blob/25dcb06f464dc11b5e589ab6859dfcc487f8f3ef/core/models.py#L1771
    
    #ebfile = EbookFile(edition=edition, file=file_, format='mobi')
    #ebfile.save()

    # maybe need to create an ebook pointing to  ebookFile ?
    # copy metadata from sister ebook
    
    ebfile_url = default_storage.url(file_.name)
    #print (ebfile_url)
    
    ebook = Ebook(url=ebfile_url,
                  format="mobi", 
                  provider="Unglue.it",
                  rights=sister_ebook.rights, 
                  edition=edition)
    ebook.save()
    
    return ebook         
