from django.test import TestCase

from regluit.core import books

class TestBooks(TestCase):

    def test_get_edition(self):
        edition = books.get_edition(isbn='0441012035')
        self.assertEqual(edition['title'], 'Neuromancer')
        self.assertEqual(edition['publication_date'], '2004')
        self.assertEqual(edition['publisher'], 'Ace Books')
        self.assertEqual(edition['page_count'], 371)
        self.assertEqual(edition['authors'], ['William Gibson'])
        self.assertEqual(edition['isbn_10'], ['0441012035'])
        self.assertEqual(edition['isbn_13'], ['9780441012039'])
        self.assertEqual(edition['google_books_id'], '2NyiPwAACAAJ')
        self.assertTrue('Fiction / Science Fiction / General' in edition['categories'])
        self.assertTrue('The future blazed into existence with each deliberate word' in edition['description'])
        self.assertEqual(edition['cover_image_url'], 'http://bks3.books.google.com/books?id=2NyiPwAACAAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api')

    def test_get_work(self):
        work = books.get_work(isbn='0441012035')
        self.assertEqual(work['title'], 'Neuromancer')

