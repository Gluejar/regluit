"""Tests for the close_out_b2u command (closing out campaigns 126 and 137)."""
import hashlib
import os
import tempfile
import zipfile
from datetime import datetime
from io import BytesIO, StringIO
from unittest import mock

from django.core import mail
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from regluit.core import signals
from regluit.core.management.commands import close_out_b2u
from regluit.core.models import (
    Campaign, CampaignAction, Ebook, EbookFile, Edition, Work,
)
from regluit.core.parameters import BUY2UNGLUE, THANKS

CONTAINER = (
    '<?xml version="1.0"?>'
    '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
    '<rootfiles><rootfile full-path="OEBPS/content.opf" '
    'media-type="application/oebps-package+xml"/></rootfiles></container>')
OPF = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="bookid" version="2.0">'
    '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
    '<dc:title>A sold book</dc:title><dc:language>en</dc:language>'
    '<dc:identifier id="bookid">urn:uuid:0000</dc:identifier>'
    '<dc:rights>All rights reserved</dc:rights></metadata>'
    '<manifest>'
    '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>'
    '<item id="title" href="title.xhtml" media-type="application/xhtml+xml"/>'
    '<item id="one" href="one.xhtml" media-type="application/xhtml+xml"/>'
    '</manifest>'
    '<spine toc="ncx"><itemref idref="title"/><itemref idref="one"/></spine>'
    '<guide><reference type="text" title="title" href="title.xhtml"/></guide>'
    '</package>')
NCX = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1"><head/>'
    '<docTitle><text>A sold book</text></docTitle><navMap>'
    '<navPoint id="n1" playOrder="1"><navLabel><text>One</text></navLabel>'
    '<content src="one.xhtml"/></navPoint></navMap></ncx>')
PAGE = '<html xmlns="http://www.w3.org/1999/xhtml"><head><title>t</title></head><body><p>%s</p></body></html>'

CC_URL = 'https://creativecommons.org/licenses/by-nc-nd/3.0/'

# the command's own list, copied at import, before any test swaps it
REAL_ALLOWED = dict(close_out_b2u.ALLOWED)
REAL_PAGE_EDITS = dict(close_out_b2u.PAGE_EDITS)


def small_epub():
    """a minimal epub, as bytes"""
    out = BytesIO()
    with zipfile.ZipFile(out, 'w') as book:
        book.writestr('mimetype', 'application/epub+zip')
        book.writestr('META-INF/container.xml', CONTAINER)
        book.writestr('OEBPS/content.opf', OPF)
        book.writestr('OEBPS/toc.ncx', NCX)
        book.writestr('OEBPS/title.xhtml', PAGE % 'title')
        book.writestr('OEBPS/one.xhtml', PAGE % 'one')
    return out.getvalue()


def sha256(data):
    return hashlib.sha256(data).hexdigest()


# files go to memory, not to disk or S3
@override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.InMemoryStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})
class CloseOutB2UTests(TestCase):

    def setUp(self):
        self.work = Work.objects.create(title="A sold book", language='en')
        self.edition = Edition.objects.create(work=self.work, title="A sold book")
        self.campaign = Campaign.objects.create(
            work=self.work, type=BUY2UNGLUE, status='ACTIVE', license='CC BY-NC-ND',
            target=30000, dollar_per_day=1.7858, activated=datetime(2014, 1, 15),
            cc_date_initial=datetime(2060, 1, 14), deadline=datetime(2060, 1, 14),
            description="a legacy campaign")
        self.original_bytes = small_epub()
        self.original = EbookFile(edition=self.edition, format='epub')
        self.original.file.save('ebf/original.epub', ContentFile(self.original_bytes))

        # the command only accepts listed campaigns; list this one
        allowed = mock.patch.dict(
            close_out_b2u.ALLOWED, {self.campaign.id: self.work.id}, clear=True)
        allowed.start()
        self.addCleanup(allowed.stop)

        self.tmp = tempfile.mkdtemp()
        self.addCleanup(self.remove_tmp)

    def remove_tmp(self):
        for name in os.listdir(self.tmp):
            os.remove(os.path.join(self.tmp, name))
        os.rmdir(self.tmp)

    # ---- helpers -----------------------------------------------------------

    def run_command(self, *args):
        out = StringIO()
        call_command('close_out_b2u', *args, stdout=out)
        return out.getvalue()

    def state(self):
        """everything the command may change, for before/after comparisons"""
        self.campaign.refresh_from_db()
        self.work.refresh_from_db()
        return {
            'status': self.campaign.status,
            'target': self.campaign.target,
            'cc_date_initial': self.campaign.cc_date_initial,
            'dollar_per_day': self.campaign.dollar_per_day,
            'is_free': self.work.is_free,
            'files': list(EbookFile.objects.values_list('id', 'file', 'ebook_id').order_by('id')),
            'records': list(Ebook.objects.values_list('id', 'url', 'active').order_by('id')),
            'actions': list(CampaignAction.objects.values_list('id', 'type').order_by('id')),
        }

    def build(self, name='licensed.epub'):
        """run build-epub; returns (path, bytes)"""
        path = os.path.join(self.tmp, name)
        self.run_command('build-epub', str(self.campaign.id), '--out', path)
        with open(path, 'rb') as built:
            return path, built.read()

    def publish(self, *extra):
        path, data = self.build()
        return self.run_command(
            'publish', str(self.campaign.id), '--epub', path, '--sha256', sha256(data), *extra)

    def stored_original(self):
        self.original.refresh_from_db()
        self.original.file.open('rb')
        try:
            return self.original.file.read()
        finally:
            self.original.file.close()

    # ---- the list ----------------------------------------------------------

    def test_campaign_not_on_the_list_is_refused(self):
        other = Campaign.objects.create(
            work=self.work, type=BUY2UNGLUE, status='ACTIVE', description="another")
        for step in (['look'], ['succeed', '--apply']):
            with self.assertRaisesMessage(CommandError, "not on the list"):
                self.run_command(step[0], str(other.id), *step[1:])

    def test_listed_campaign_on_the_wrong_book_is_refused(self):
        with mock.patch.dict(close_out_b2u.ALLOWED, {self.campaign.id: self.work.id + 1}):
            with self.assertRaisesMessage(CommandError, "belongs to work"):
                self.run_command('look', str(self.campaign.id))

    def test_campaign_of_another_type_is_refused(self):
        Campaign.objects.filter(pk=self.campaign.pk).update(type=THANKS)
        with self.assertRaisesMessage(CommandError, "not a Buy-to-Unglue campaign"):
            self.run_command('look', str(self.campaign.id))

    def test_the_real_list_is_the_two_campaigns(self):
        # setUp swaps the list for the test campaign; REAL_ALLOWED was copied before that
        self.assertEqual(REAL_ALLOWED, {126: 128685, 137: 137647})

    # ---- look --------------------------------------------------------------

    def test_look_changes_nothing_and_reports_the_start_state(self):
        before = self.state()
        output = self.run_command('look', str(self.campaign.id), '--hashes')
        self.assertEqual(self.state(), before)
        self.assertIn("status            ACTIVE", output)
        self.assertIn("file %s" % self.original.id, output)
        self.assertIn("not linked to a record", output)
        self.assertIn(sha256(self.original_bytes), output)
        self.assertIn("ebook records: none", output)
        self.assertIn("[no ] campaign is SUCCESSFUL", output)
        self.assertIn("[yes] the original stored epub is still there", output)
        self.assertIn("1 of 6 end-state checks hold. Nothing was changed.", output)

    def test_look_after_both_steps_shows_the_end_state(self):
        self.publish('--apply')
        self.run_command('succeed', str(self.campaign.id), '--apply')
        output = self.run_command('look', str(self.campaign.id))
        self.assertNotIn("[no ]", output)
        self.assertIn("6 of 6 end-state checks hold", output)

    # ---- build-epub --------------------------------------------------------

    def test_build_epub_writes_a_licensed_copy_and_touches_nothing_else(self):
        before = self.state()
        path = os.path.join(self.tmp, 'licensed.epub')
        output = self.run_command('build-epub', str(self.campaign.id), '--out', path)
        self.assertEqual(self.state(), before)
        # the stored original is byte-for-byte what it was
        self.assertEqual(self.stored_original(), self.original_bytes)

        with open(path, 'rb') as built:
            data = built.read()
        self.assertIn(sha256(data), output)
        book = zipfile.ZipFile(BytesIO(data))
        self.assertIn('OEBPS/cc_license.xhtml', book.namelist())
        page = book.read('OEBPS/cc_license.xhtml').decode('utf-8')
        self.assertIn(CC_URL, page)
        self.assertIn("Attribution-NonCommercial-NoDerivs", page)
        # no free-date in it: that date is decades away
        self.assertNotIn("2059", page)
        self.assertNotIn("2060", page)
        # the book's own pages are still there
        self.assertEqual(book.read('OEBPS/one.xhtml').decode('utf-8'), PAGE % 'one')
        # the license is the only rights line; "All rights reserved" was replaced, and said so
        self.assertEqual(close_out_b2u.rights_lines(data), [CC_URL])
        self.assertIn("rights lines it replaced: All rights reserved", output)

    def test_only_the_three_regenerated_files_are_exempt_from_the_comparison(self):
        _, _, rewritten, pages = close_out_b2u.add_license_page(self.original_bytes, self.campaign)
        self.assertEqual(
            rewritten, {'META-INF/container.xml', 'OEBPS/content.opf', 'OEBPS/toc.ncx'})
        self.assertEqual(pages, {})  # no page edits are listed for the test campaign

    # ---- build-epub: wording on the book's own pages -------------------------

    def page_edit(self, old='<p>one</p>', new='<p>one, under a %(name)s license: %(url)s</p>',
                  name='OEBPS/one.xhtml'):
        """list one page edit for the test campaign, for the length of a test"""
        edits = mock.patch.dict(close_out_b2u.PAGE_EDITS, {self.campaign.id: [(name, old, new)]})
        edits.start()
        self.addCleanup(edits.stop)

    def test_the_real_page_edits_are_one_paragraph_of_one_book(self):
        self.assertEqual(list(REAL_PAGE_EDITS), [126])
        (name, old, new), = REAL_PAGE_EDITS[126]
        self.assertEqual(name, 'OEBPS/Text/copyright.html')
        self.assertTrue(old.startswith('All rights reserved. No part of this publication'))
        self.assertTrue(old.endswith('without the prior written permission of the Publisher.'))
        self.assertTrue(new.startswith('Some rights reserved.'))

    def test_build_epub_applies_a_listed_page_edit_and_nothing_else(self):
        self.page_edit()
        path = os.path.join(self.tmp, 'edited.epub')
        output = self.run_command('build-epub', str(self.campaign.id), '--out', path)
        book = zipfile.ZipFile(path)
        page = book.read('OEBPS/one.xhtml').decode('utf-8')
        self.assertEqual(page, PAGE % (
            'one, under a Creative Commons Attribution-NonCommercial-NoDerivs 3.0 Unported '
            '(CC BY-NC-ND 3.0) license: ' + CC_URL))
        # the other page of the book is untouched, and so is the stored original
        self.assertEqual(book.read('OEBPS/title.xhtml').decode('utf-8'), PAGE % 'title')
        self.assertEqual(self.stored_original(), self.original_bytes)
        self.assertIn("page edited: OEBPS/one.xhtml", output)
        self.assertIn("was: <p>one</p>", output)

    def test_build_epub_refuses_when_the_text_to_replace_is_not_there(self):
        self.page_edit(old='<p>not in the book</p>')
        path = os.path.join(self.tmp, 'x.epub')
        with self.assertRaisesMessage(CommandError, "found 0 times in OEBPS/one.xhtml, expected once"):
            self.run_command('build-epub', str(self.campaign.id), '--out', path)
        self.assertFalse(os.path.exists(path))

    def test_build_epub_refuses_when_the_text_to_replace_is_there_twice(self):
        self.page_edit(old='p>')  # appears in both the opening and the closing tag
        path = os.path.join(self.tmp, 'x.epub')
        with self.assertRaisesMessage(CommandError, "expected once"):
            self.run_command('build-epub', str(self.campaign.id), '--out', path)
        self.assertFalse(os.path.exists(path))

    def test_build_epub_refuses_when_the_page_to_edit_is_not_in_the_book(self):
        self.page_edit(name='OEBPS/missing.xhtml')
        path = os.path.join(self.tmp, 'x.epub')
        with self.assertRaisesMessage(CommandError, "OEBPS/missing.xhtml is not in the book"):
            self.run_command('build-epub', str(self.campaign.id), '--out', path)
        self.assertFalse(os.path.exists(path))

    def test_build_epub_refuses_if_a_file_of_the_book_came_out_different(self):
        real = close_out_b2u.add_license_page

        def tampering(original_bytes, campaign):
            data, replaced, rewritten, pages = real(original_bytes, campaign)
            out = BytesIO()
            source = zipfile.ZipFile(BytesIO(data))
            with zipfile.ZipFile(out, 'w') as changed:
                for name in source.namelist():
                    body = b'changed' if name == 'OEBPS/one.xhtml' else source.read(name)
                    changed.writestr(name, body)
            return out.getvalue(), replaced, rewritten, pages

        path = os.path.join(self.tmp, 'x.epub')
        with mock.patch.object(close_out_b2u, 'add_license_page', tampering):
            with self.assertRaisesMessage(CommandError, "OEBPS/one.xhtml differs from the original"):
                self.run_command('build-epub', str(self.campaign.id), '--out', path)
        self.assertFalse(os.path.exists(path))

    def test_build_epub_compresses_the_book_and_keeps_mimetype_first(self):
        _, data = self.build()
        entries = zipfile.ZipFile(BytesIO(data)).infolist()
        self.assertEqual(entries[0].filename, 'mimetype')
        self.assertEqual(entries[0].compress_type, zipfile.ZIP_STORED)
        for entry in entries[1:]:
            self.assertEqual(entry.compress_type, zipfile.ZIP_DEFLATED, entry.filename)
        self.assertEqual(len({e.filename for e in entries}), len(entries))

    def test_build_epub_puts_the_license_page_second_in_reading_order(self):
        _, data = self.build()
        opf = zipfile.ZipFile(BytesIO(data)).read('OEBPS/content.opf').decode('utf-8')
        spine = opf[opf.index('<spine'):opf.index('</spine>')]
        self.assertEqual(spine.count('itemref'), 3)
        self.assertLess(spine.index('idref="title"'), spine.index('idref="id_'))
        self.assertLess(spine.index('idref="id_'), spine.index('idref="one"'))

    def test_build_epub_will_not_overwrite_a_file(self):
        path, data = self.build()
        with self.assertRaisesMessage(CommandError, "already exists"):
            self.run_command('build-epub', str(self.campaign.id), '--out', path)
        with open(path, 'rb') as built:
            self.assertEqual(built.read(), data)

    def test_build_epub_needs_exactly_one_stored_epub(self):
        second = EbookFile(edition=self.edition, format='epub')
        second.file.save('ebf/second.epub', ContentFile(self.original_bytes))
        with self.assertRaisesMessage(CommandError, "expected exactly one stored epub"):
            self.run_command(
                'build-epub', str(self.campaign.id), '--out', os.path.join(self.tmp, 'x.epub'))
        self.assertEqual(os.listdir(self.tmp), [])

    # ---- publish -----------------------------------------------------------

    def test_publish_without_apply_changes_nothing(self):
        before = self.state()
        output = self.publish()
        self.assertEqual(self.state(), before)
        self.assertIn("WOULD store the file", output)
        self.assertIn("Nothing changed", output)

    def test_publish_makes_the_book_free_with_a_record_pointing_at_the_stored_file(self):
        path, data = self.build()
        output = self.run_command(
            'publish', str(self.campaign.id), '--epub', path, '--sha256', sha256(data), '--apply')

        ebook = Ebook.objects.get()
        self.assertTrue(ebook.active)
        self.assertEqual(ebook.provider, 'Unglue.it')
        self.assertEqual(ebook.rights, 'CC BY-NC-ND')
        self.assertEqual(ebook.format, 'epub')
        self.assertEqual(ebook.edition, self.edition)
        self.assertEqual(ebook.filesize, len(data))

        new_file = EbookFile.objects.exclude(pk=self.original.pk).get()
        self.assertEqual(new_file.ebook, ebook)
        self.assertEqual(ebook.url, new_file.file.url)
        self.assertNotIn('/unglued/', ebook.url)
        new_file.file.open('rb')
        self.assertEqual(new_file.file.read(), data)
        new_file.file.close()

        # the original is untouched and still not linked
        self.assertEqual(self.stored_original(), self.original_bytes)
        self.assertIsNone(self.original.ebook_id)

        self.work.refresh_from_db()
        self.assertTrue(self.work.is_free)
        # the campaign itself has not moved
        self.campaign.refresh_from_db()
        self.assertEqual(self.campaign.status, 'ACTIVE')
        self.assertFalse(CampaignAction.objects.exists())
        self.assertIn("PUBLISHED", output)
        self.assertIn("record %s" % ebook.id, output)

    def test_publish_refuses_a_file_that_is_not_the_approved_one(self):
        path, data = self.build()
        before = self.state()
        with self.assertRaisesMessage(CommandError, "not the approved file"):
            self.run_command(
                'publish', str(self.campaign.id), '--epub', path,
                '--sha256', sha256(data + b'x'), '--apply')
        self.assertEqual(self.state(), before)

    def test_publish_refuses_a_file_that_is_not_an_epub(self):
        path = os.path.join(self.tmp, 'notes.epub')
        with open(path, 'wb') as junk:
            junk.write(b'not a book')
        before = self.state()
        with self.assertRaisesMessage(CommandError, "does not open as an epub"):
            self.run_command(
                'publish', str(self.campaign.id), '--epub', path,
                '--sha256', sha256(b'not a book'), '--apply')
        self.assertEqual(self.state(), before)

    def test_publish_a_second_time_is_refused_and_changes_nothing(self):
        path, data = self.build()
        args = ('publish', str(self.campaign.id), '--epub', path, '--sha256', sha256(data), '--apply')
        self.run_command(*args)
        before = self.state()
        with self.assertRaisesMessage(CommandError, "already published"):
            self.run_command(*args)
        self.assertEqual(self.state(), before)

    def test_publish_refuses_when_the_book_already_has_an_active_record(self):
        path, data = self.build()
        Ebook.objects.create(
            edition=self.edition, format='pdf', provider='elsewhere', rights='CC BY',
            url='https://example.org/book.pdf')
        before = self.state()
        with self.assertRaisesMessage(CommandError, "already has active ebook records"):
            self.run_command(
                'publish', str(self.campaign.id), '--epub', path, '--sha256', sha256(data), '--apply')
        self.assertEqual(self.state(), before)

    def test_publish_refuses_when_the_campaign_is_not_active(self):
        path, data = self.build()
        Campaign.objects.filter(pk=self.campaign.pk).update(status='SUSPENDED')
        before = self.state()
        with self.assertRaisesMessage(CommandError, "expected ACTIVE"):
            self.run_command(
                'publish', str(self.campaign.id), '--epub', path, '--sha256', sha256(data), '--apply')
        self.assertEqual(self.state(), before)

    def test_publish_refuses_an_epub_that_does_not_carry_the_license(self):
        # the unchanged original: a real epub, right hash, "All rights reserved"
        path = os.path.join(self.tmp, 'unlicensed.epub')
        with open(path, 'wb') as other:
            other.write(self.original_bytes)
        before = self.state()
        with self.assertRaisesMessage(CommandError, "no rights line naming the campaign's license"):
            self.run_command(
                'publish', str(self.campaign.id), '--epub', path,
                '--sha256', sha256(self.original_bytes), '--apply')
        self.assertEqual(self.state(), before)

    def test_publish_that_fails_after_storing_names_the_leftover_file(self):
        path, data = self.build()
        before = self.state()
        out = StringIO()
        with mock.patch.object(Ebook.objects, 'create', side_effect=RuntimeError("database trouble")):
            with self.assertRaisesMessage(RuntimeError, "database trouble"):
                call_command(
                    'close_out_b2u', 'publish', str(self.campaign.id), '--epub', path,
                    '--sha256', sha256(data), '--apply', stdout=out)
        # the database is as it was, and the output says which file was left behind
        self.assertEqual(self.state(), before)
        self.assertIn("NOT PUBLISHED", out.getvalue())
        self.assertRegex(out.getvalue(), r"not referenced by anything: ebf/\w+\.epub")

    # ---- succeed -----------------------------------------------------------

    def test_succeed_before_publish_is_refused(self):
        before = self.state()
        with self.assertRaisesMessage(CommandError, "run publish first"):
            self.run_command('succeed', str(self.campaign.id), '--apply')
        self.assertEqual(self.state(), before)

    def test_succeed_without_apply_changes_nothing(self):
        self.publish('--apply')
        before = self.state()
        output = self.run_command('succeed', str(self.campaign.id))
        self.assertEqual(self.state(), before)
        self.assertIn("WOULD set the status to SUCCESSFUL", output)
        self.assertIn("No notice is sent", output)

    def test_succeed_marks_the_campaign_and_leaves_its_figures_alone(self):
        self.publish('--apply')
        before = self.state()
        # the app's success notice hangs off this signal; it must not fire
        with mock.patch.object(signals.successful_campaign, 'send') as send:
            output = self.run_command('succeed', str(self.campaign.id), '--apply')
        send.assert_not_called()
        after = self.state()
        self.assertEqual(after['status'], 'SUCCESSFUL')
        self.assertEqual(
            list(CampaignAction.objects.values_list('campaign_id', 'type')),
            [(self.campaign.id, 'succeeded')])
        for unchanged in ('target', 'cc_date_initial', 'dollar_per_day', 'is_free', 'files', 'records'):
            self.assertEqual(after[unchanged], before[unchanged])
        self.assertTrue(self.campaign.success_date)
        self.assertEqual(len(mail.outbox), 0)
        self.assertIn("No notice was sent", output)

    def test_succeed_refuses_when_another_active_record_is_on_the_book(self):
        self.publish('--apply')
        Ebook.objects.create(
            edition=self.edition, format='pdf', provider='elsewhere', rights='CC BY',
            url='https://example.org/book.pdf')
        before = self.state()
        with self.assertRaisesMessage(CommandError, "other active ebook records"):
            self.run_command('succeed', str(self.campaign.id), '--apply')
        self.assertEqual(self.state(), before)

    def test_succeed_refuses_when_the_original_is_gone(self):
        self.publish('--apply')
        EbookFile.objects.filter(pk=self.original.pk).delete()
        before = self.state()
        with self.assertRaisesMessage(CommandError, "expected two stored epubs"):
            self.run_command('succeed', str(self.campaign.id), '--apply')
        self.assertEqual(self.state(), before)

    def test_succeed_a_second_time_is_refused_and_changes_nothing(self):
        self.publish('--apply')
        self.run_command('succeed', str(self.campaign.id), '--apply')
        before = self.state()
        with self.assertRaisesMessage(CommandError, "expected ACTIVE"):
            self.run_command('succeed', str(self.campaign.id), '--apply')
        self.assertEqual(self.state(), before)

    def test_succeed_refuses_if_the_published_record_was_deactivated(self):
        self.publish('--apply')
        Ebook.objects.get().deactivate()
        before = self.state()
        with self.assertRaisesMessage(CommandError, "run publish first"):
            self.run_command('succeed', str(self.campaign.id), '--apply')
        self.assertEqual(self.state(), before)
