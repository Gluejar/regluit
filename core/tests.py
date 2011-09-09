from django.test import TestCase

from regluit.core import books

class TestBooks(TestCase):

    def test_add_book(self):
        edition = books.add_book(isbn='0441012035')
        self.assertEqual(edition.title, 'Neuromancer')
        self.assertEqual(edition.publication_date, '2004')
        self.assertEqual(edition.publisher, 'Ace Books')

        self.assertEqual(edition.isbn_10, '0441012035')
        self.assertEqual(edition.isbn_13, None)

        covers = edition.covers.all()
        self.assertEqual(len(covers), 1)
        self.assertEqual(covers[0].openlibrary_id, 284192)

        work = edition.work
        self.assertTrue(work)
        self.assertEqual(work.authors.all()[0].name, 'William F. Gibson')

        subject_names = [subject.name for subject in work.subjects.all()]
        self.assertTrue(len(subject_names) > 15)
        self.assertTrue('Fiction' in subject_names)


