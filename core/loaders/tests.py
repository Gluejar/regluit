from django.conf import settings
from django.test import TestCase
from regluit.core.models import Ebook, Edition, Work
from .harvest import dl_online

class LoaderTests(TestCase):
    def setUp(self):
        pass

    def test_downloads(self):
        if not (settings.TEST_INTEGRATION):
            return

        work = Work(title="online work")
        work.save()

        edition = Edition(work=work)
        edition.save()

        dropbox_url = 'https://www.dropbox.com/s/azaztyvgf6b98bc/stellar-consensus-protocol.pdf?dl=0'
        dropbox_ebook = Ebook.objects.create(format='online', url=dropbox_url, edition=edition)
        dropbox_ebf, new_ebf = dl_online(dropbox_ebook)
        self.assertTrue(dropbox_ebf.ebook.filesize)

        jbe_url = 'https://www.jbe-platform.com/content/books/9789027295958'
        jbe_ebook = Ebook.objects.create(format='online', url=jbe_url, edition=edition, 
                                         provider='jbe-platform.com')
        jbe_ebf, new_ebf = dl_online(jbe_ebook)
        self.assertTrue(jbe_ebf.ebook.filesize)
