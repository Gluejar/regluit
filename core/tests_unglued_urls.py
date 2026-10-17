"""Tests for the fix_unglued_ebook_urls command (#1283)."""
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from regluit.core.models import Ebook, EbookFile, Edition, Work

OLD = 'https://unglue.it/work/%s/unglued/%s/'


class FixUngluedEbookUrlsTests(TestCase):
    """Ebook records left pointing at the removed /work/<id>/unglued/<format>/
    address are pointed at their stored file, and nothing else is touched."""

    def setUp(self):
        self.work = Work.objects.create(title="Freed book", language='en')
        self.edition = Edition.objects.create(work=self.work, title="Freed book")

    def make_record(self, fmt='epub', active=True, edition=None):
        edition = edition or self.edition
        return Ebook.objects.create(
            edition=edition, format=fmt, provider='Unglue.it', rights='CC0',
            url=OLD % (edition.work_id, fmt), active=active)

    def make_file(self, name, fmt='epub', ebook=None, edition=None):
        # a stored-file record by name; nothing is written to storage
        return EbookFile.objects.create(
            edition=edition or self.edition, format=fmt, file=name, ebook=ebook)

    def run_command(self, *args):
        out = StringIO()
        call_command('fix_unglued_ebook_urls', *args, stdout=out)
        return out.getvalue()

    def test_default_run_reports_and_changes_nothing(self):
        ebook = self.make_record()
        ebf = self.make_file('ebf/aaa.epub', ebook=ebook)
        output = self.run_command()
        ebook.refresh_from_db()
        self.assertEqual(ebook.url, OLD % (self.work.id, 'epub'))
        self.assertIn("WOULD FIX ebook %s" % ebook.id, output)
        self.assertIn(ebf.file.url, output)
        self.assertIn("would fix 1, skipped 0", output)
        self.assertIn("nothing changed", output)

    def test_apply_points_the_record_at_its_stored_file(self):
        ebook = self.make_record()
        ebf = self.make_file('ebf/aaa.epub', ebook=ebook)
        output = self.run_command('--apply')
        ebook.refresh_from_db()
        self.assertEqual(ebook.url, ebf.file.url)
        self.assertNotIn('/unglued/', ebook.url)
        self.assertTrue(ebook.active)
        # the old address is in the output, so the change can be put back
        self.assertIn(OLD % (self.work.id, 'epub'), output)
        self.assertIn("fixed 1, skipped 0", output)

    def test_each_format_gets_its_own_file(self):
        epub = self.make_record('epub')
        mobi = self.make_record('mobi')
        epub_file = self.make_file('ebf/aaa.epub', 'epub', ebook=epub)
        mobi_file = self.make_file('ebf/bbb.mobi', 'mobi', ebook=mobi)
        self.run_command('--apply')
        epub.refresh_from_db()
        mobi.refresh_from_db()
        self.assertEqual(epub.url, epub_file.file.url)
        self.assertEqual(mobi.url, mobi_file.file.url)

    def test_older_files_are_ignored_when_the_newest_is_the_linked_one(self):
        ebook = self.make_record()
        self.make_file('ebf/old.epub')  # an earlier upload, not linked
        newest = self.make_file('ebf/new.epub', ebook=ebook)
        self.run_command('--apply')
        ebook.refresh_from_db()
        self.assertEqual(ebook.url, newest.file.url)

    def test_second_run_does_nothing(self):
        ebook = self.make_record()
        self.make_file('ebf/aaa.epub', ebook=ebook)
        self.run_command('--apply')
        ebook.refresh_from_db()
        fixed_url = ebook.url
        output = self.run_command('--apply')
        ebook.refresh_from_db()
        self.assertEqual(ebook.url, fixed_url)
        self.assertIn("fixed 0, skipped 0", output)

    def test_inactive_record_is_left_alone(self):
        ebook = self.make_record(active=False)
        self.make_file('ebf/aaa.epub', ebook=ebook)
        output = self.run_command('--apply')
        ebook.refresh_from_db()
        self.assertEqual(ebook.url, OLD % (self.work.id, 'epub'))
        self.assertIn("fixed 0, skipped 0", output)

    def test_record_with_no_stored_file_is_skipped(self):
        ebook = self.make_record()
        self.make_file('ebf/bbb.mobi', 'mobi')  # a different format does not count
        output = self.run_command('--apply')
        ebook.refresh_from_db()
        self.assertEqual(ebook.url, OLD % (self.work.id, 'epub'))
        self.assertIn("SKIP ebook %s" % ebook.id, output)
        self.assertIn("no stored file", output)
        self.assertIn("fixed 0, skipped 1", output)

    def test_record_is_skipped_when_the_newest_file_is_not_its_own(self):
        ebook = self.make_record()
        self.make_file('ebf/linked.epub', ebook=ebook)
        self.make_file('ebf/later.epub')  # newer, linked to nothing
        output = self.run_command('--apply')
        ebook.refresh_from_db()
        self.assertEqual(ebook.url, OLD % (self.work.id, 'epub'))
        self.assertIn("is not linked to this record", output)
        self.assertIn("fixed 0, skipped 1", output)

    def test_other_addresses_are_never_touched(self):
        # a stored-file address, an outside address, and one that only mentions /unglued/
        own_file = Ebook.objects.create(
            edition=self.edition, format='epub', provider='Unglue.it',
            url='https://example-bucket.s3.amazonaws.com/ebf/zzz.epub')
        outside = Ebook.objects.create(
            edition=self.edition, format='pdf', provider='Elsewhere',
            url='https://example.org/books/unglued/guide.pdf')
        self.make_file('ebf/zzz.epub', ebook=own_file)
        self.make_file('ebf/guide.pdf', 'pdf', ebook=outside)
        output = self.run_command('--apply')
        own_file.refresh_from_db()
        outside.refresh_from_db()
        self.assertEqual(own_file.url, 'https://example-bucket.s3.amazonaws.com/ebf/zzz.epub')
        self.assertEqual(outside.url, 'https://example.org/books/unglued/guide.pdf')
        self.assertIn("fixed 0, skipped 0", output)

    def test_address_naming_another_book_or_format_is_skipped(self):
        # same shape as the old address, but not this record's own book and format
        wrong_book = Ebook.objects.create(
            edition=self.edition, format='epub', provider='Unglue.it',
            url=OLD % (self.work.id + 999, 'epub'))
        wrong_format = Ebook.objects.create(
            edition=self.edition, format='mobi', provider='Unglue.it',
            url=OLD % (self.work.id, 'pdf'))
        self.make_file('ebf/aaa.epub', 'epub', ebook=wrong_book)
        self.make_file('ebf/bbb.mobi', 'mobi', ebook=wrong_format)
        output = self.run_command('--apply')
        wrong_book.refresh_from_db()
        wrong_format.refresh_from_db()
        self.assertEqual(wrong_book.url, OLD % (self.work.id + 999, 'epub'))
        self.assertEqual(wrong_format.url, OLD % (self.work.id, 'pdf'))
        self.assertEqual(output.count("names a different book or format"), 2)
        self.assertIn("fixed 0, skipped 2", output)

    def test_same_shaped_address_on_another_site_is_never_touched(self):
        elsewhere = Ebook.objects.create(
            edition=self.edition, format='epub', provider='Elsewhere',
            url='https://example.org/work/%s/unglued/epub/' % self.work.id)
        self.make_file('ebf/aaa.epub', ebook=elsewhere)
        output = self.run_command('--apply')
        elsewhere.refresh_from_db()
        self.assertEqual(elsewhere.url, 'https://example.org/work/%s/unglued/epub/' % self.work.id)
        self.assertIn("fixed 0, skipped 0", output)

    def test_the_test_site_address_counts_as_ours(self):
        ebook = Ebook.objects.create(
            edition=self.edition, format='epub', provider='Unglue.it',
            url='https://test.unglue.it/work/%s/unglued/epub/' % self.work.id)
        ebf = self.make_file('ebf/aaa.epub', ebook=ebook)
        self.run_command('--apply')
        ebook.refresh_from_db()
        self.assertEqual(ebook.url, ebf.file.url)

    def test_nothing_is_written_if_the_record_changed_after_it_was_read(self):
        from regluit.core.management.commands.fix_unglued_ebook_urls import Command
        ebook = self.make_record()
        # someone else edits the address after the command has read the record
        Ebook.objects.filter(pk=ebook.pk).update(url='https://example.org/edited.epub')
        self.assertFalse(Command.repoint(ebook, 'https://example-bucket.s3.amazonaws.com/ebf/aaa.epub'))
        ebook.refresh_from_db()
        self.assertEqual(ebook.url, 'https://example.org/edited.epub')

    def test_nothing_is_written_if_the_record_was_deactivated_after_it_was_read(self):
        from regluit.core.management.commands.fix_unglued_ebook_urls import Command
        ebook = self.make_record()
        Ebook.objects.filter(pk=ebook.pk).update(active=False)
        self.assertFalse(Command.repoint(ebook, 'https://example-bucket.s3.amazonaws.com/ebf/aaa.epub'))
        ebook.refresh_from_db()
        self.assertEqual(ebook.url, OLD % (self.work.id, 'epub'))

    def test_a_file_on_another_book_does_not_count(self):
        ebook = self.make_record()
        other_work = Work.objects.create(title="Another book", language='en')
        other_edition = Edition.objects.create(work=other_work, title="Another book")
        self.make_file('ebf/other.epub', edition=other_edition)
        output = self.run_command('--apply')
        ebook.refresh_from_db()
        self.assertEqual(ebook.url, OLD % (self.work.id, 'epub'))
        self.assertIn("no stored file", output)
