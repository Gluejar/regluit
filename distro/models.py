import logging
import requests
from ftplib import FTP, FTP_TLS
from StringIO import StringIO
from django.db import models

logger = logging.getLogger(__name__)

class Target(models.Model):
    name = models.CharField(max_length=30)
    host = models.CharField(max_length=60)
    pw = models.CharField(max_length=30)
    user = models.CharField(max_length=30)
    protocol = models.CharField(max_length=10, default='ftp')
    formats = models.ManyToManyField('Format', related_name='targets')
    
    def __unicode__(self):
        return self.name
    
    def get_ftp(self):
        if self.protocol == 'secure':
            _ftp =  FTP_TLS(self.host, self.user, self.pw)
            _ftp.prot_p()
        else:
            _ftp = FTP(self.host, self.user, self.pw)
        return _ftp
                
    def push(self, book, new=False):
        pushed_formats = []
        pushed_isbns = set()
        for ebook in book.ebooks():
            isbn = ebook.edition.isbn_13 if ebook.edition.isbn_13 else book.first_isbn_13()
            if isbn and self.formats.filter(name=ebook.format).exists() and ebook.format not in pushed_formats:
                dont_push = new and Deposit.objects.filter(isbn=isbn, target=self, format=ebook.format).exists()
                if not dont_push:
                    ebfile = ebook.get_archive()
                    if ebfile:
                        self.push_file(u'{}.{}'.format(isbn,ebook.format), ebfile)
                        ebfile.close()
                        pushed_formats.append(ebook.format)
                        pushed_isbns.add(isbn)
                        Deposit.objects.create(target=self, isbn=isbn, format=ebook.format)
                    else:
                        logger.error('no file available for ebook {}'.format(ebook.id))
        if pushed_isbns:
            cover = book.cover_image_large()
            if cover:
                r = requests.get(cover)
                for isbn in pushed_isbns:
                    self.push_file(u'{}.{}'.format(isbn,'jpg'), StringIO(r.content))
            else:
                logger.error('no cover available for {}'.format(book))
        return pushed_isbns
            
    def push_file(self, filename, file_to_push):
        self.get_ftp().storbinary(u'STOR {}'.format(filename), file_to_push)
        
            
class Deposit(models.Model):
    target = models.ForeignKey(Target, on_delete=models.CASCADE, related_name="deposits")
    isbn = models.CharField(max_length=13)
    format = models.CharField(max_length=30)
    updated = models.DateTimeField(auto_now_add=True)
    
class Format(models.Model):
    name = models.CharField(max_length=4)

    def __unicode__(self):
        return self.name
