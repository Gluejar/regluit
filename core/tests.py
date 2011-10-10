from django.test import TestCase

from regluit.core import bookloader, models, search

class TestBooks(TestCase):

    def test_add_book(self):
        # edition
        edition = bookloader.add_by_isbn('0441012035')
        self.assertEqual(edition.title, 'Neuromancer')
        self.assertEqual(edition.publication_date, '2004')
        self.assertEqual(edition.publisher, 'Ace Books')
        self.assertEqual(edition.isbn_10, '0441012035')
        self.assertEqual(edition.isbn_13, '9780441012039')
        self.assertEqual(edition.googlebooks_id, "2NyiPwAACAAJ")

        # subjects
        subject_names = [subject.name for subject in edition.subjects.all()]
        self.assertEqual(len(subject_names), 11)
        self.assertTrue('Japan' in subject_names)

        # authors
        self.assertEqual(edition.authors.all().count(), 1)
        self.assertEqual(edition.authors.all()[0].name, 'William Gibson')

        # work
        self.assertTrue(edition.work)

    def test_double_add(self):
        bookloader.add_by_isbn('0441012035')
        bookloader.add_by_isbn('0441012035')
        self.assertEqual(models.Edition.objects.all().count(), 1)
        self.assertEqual(models.Author.objects.all().count(), 1)
        self.assertEqual(models.Work.objects.all().count(), 1)
        self.assertEqual(models.Subject.objects.all().count(), 11)
        

class SearchTests(TestCase):

    def test_basic_search(self):
        results = search.gluejar_search('melville')
        self.assertEqual(len(results), 10)

        r = results[0]
        self.assertTrue(r.has_key('title'))
        self.assertTrue(r.has_key('author'))
        self.assertTrue(r.has_key('description'))
        self.assertTrue(r.has_key('image'))
        self.assertTrue(r.has_key('publisher'))
        self.assertTrue(r.has_key('isbn_10'))
        self.assertTrue(r.has_key('googlebooks_id'))

    def test_googlebooks_search(self):
        response = search.googlebooks_search('melville')
        self.assertEqual(len(response['items']), 10)
