from django.test import TestCase

from regluit.core import bookloader, models, search

class TestBooks(TestCase):

    def test_add_book(self):
        # edition
        edition = bookloader.add_book(isbn='0441012035')
        self.assertEqual(edition.title, 'Neuromancer')
        self.assertEqual(edition.publication_date, '2004')
        self.assertEqual(edition.publisher, 'Ace Books')
        self.assertEqual(edition.isbn_10, '0441012035')
        self.assertEqual(edition.isbn_13, None)
        self.assertEqual(edition.openlibrary_id, "/books/OL3305354M")

        # edition covers
        covers = edition.covers.all()
        self.assertEqual(len(covers), 1)
        self.assertEqual(covers[0].openlibrary_id, 284192)

        # work
        work = edition.work
        self.assertTrue(work)
        self.assertEqual(work.authors.all()[0].name, 'William F. Gibson')

        # subjects
        subject_names = [subject.name for subject in work.subjects.all()]
        self.assertEqual(len(subject_names), 18)
        self.assertTrue('Fiction' in subject_names)

        # authors
        author_names = [author.name for author in work.authors.all()]
        self.assertEqual(len(author_names), 1)
        self.assertEqual(author_names[0], "William F. Gibson")

    def test_double_add(self):
        bookloader.add_book(isbn='0441012035')
        bookloader.add_book(isbn='0441012035')
        self.assertEqual(models.Author.objects.all().count(), 1)
        self.assertEqual(models.Work.objects.all().count(), 1)
        self.assertEqual(models.Subject.objects.all().count(), 18)
        

class SearchTests(TestCase):

    def test_basic_search(self):
        results = search.gluejar_search('melville')
        self.assertEqual(len(results), 10)

        r = results[0]
        self.assertTrue(r.has_key('name'))
        self.assertTrue(r.has_key('author'))
        self.assertTrue(r.has_key('description'))
        self.assertTrue(r.has_key('image'))
        self.assertTrue(r.has_key('publisher'))
        self.assertTrue(r.has_key('identifier'))

        for r in results:
            for i in r['identifier']:
                self.assertTrue(i.has_key('name'))
                self.assertTrue(i.has_key('value'))

    def test_googlebooks_search(self):
        response = search.googlebooks_search('melville')
        self.assertEqual(len(response['items']), 10)
