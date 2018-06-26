from django.conf import settings
from django.test import TestCase
from regluit.core.models import Ebook, Edition, Work
from .utils import dl_online

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

        dropbox_url = 'https://www.dropbox.com/s/h5jzpb4vknk8n7w/Jakobsson_The_Troll_Inside_You_EBook.pdf?dl=0'
        dropbox_ebook = Ebook.objects.create(format='online', url=dropbox_url, edition=edition)
        dropbox_ebf, new_ebf = dl_online(dropbox_ebook)
        self.assertTrue(dropbox_ebf.ebook.filesize)

        jbe_url = 'http://www.jbe-platform.com/content/books/9789027295958'
        jbe_ebook = Ebook.objects.create(format='online', url=jbe_url, edition=edition)
        jbe_ebf, new_ebf = dl_online(jbe_ebook)
        self.assertTrue(jbe_ebf.ebook.filesize)
