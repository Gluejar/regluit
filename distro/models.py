from ftplib import FTP, FTP_TLS
from django.db import models

class Target(models.Model):
    name = models.CharField(max_length=30)
    host = models.CharField(max_length=60)
    pw = models.CharField(max_length=30)
    user = models.CharField(max_length=30)
    protocol = models.CharField(max_length=10, default='ftp')
    formats = models.ManyToManyField(Format, related_name='targets')
    
    def __unicode__(self):
        return self.name
    
    _ftp = None
    def get_ftp(self):
        if not self._ftp:
            if self.protocol == 'secure':
                self._ftp =  FTP_TLS(self.host, self.user, self.pw)
                self._ftp.prot_p()
            else:
                self._ftp = FTP(self.host, self.user, self.pw)
        return self._ftp
                
    def push(self, book):
        for ebook in book.ebooks():
            isbn = ebook.edition.isbn_13 if ebook.edition.isbn_13 else ebook.edition.work.first_isbn_13()
            if isbn and self.formats.filter(name=ebook.format).exists():
                ebfile = ebook.get_archive()
                self.get_ftp().storbinary(u'STOR {}.{}'.format(isbn,ebook.format), ebfile)
                ebfile.close()
                Depost.objects.create(target=self, isbn=isbn, format=ebook.format)

        
class Deposit(models.Model):
    target = models.ForeignKey(Target, related_name="deposits")
    isbn = models.CharField(max_length=13)
    format = models.CharField(max_length=30)
    updated = models.DateTimeField(auto_now_add=True)
    
class Format(
    name = models.CharField(max_length=4)

    def __unicode__(self):
        return self.name
