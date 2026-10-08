"""
Close out the last two Buy-to-Unglue campaigns, one explicit step at a time.

    close_out_b2u look <campaign>                  report; changes nothing
    close_out_b2u build-epub <campaign> --out F    write a CC-licensed copy to a local file
    close_out_b2u publish <campaign> --epub F --sha256 H [--apply]
    close_out_b2u succeed <campaign> [--apply]

Why a command and not the campaign's own success step: update_status() marks a
Buy-to-Unglue campaign successful only once its computed free-date has passed
(decades away for both of these), and since #1093 success no longer publishes a
free copy. This does the two things separately and on purpose: publish the
free copy, then mark the campaign successful. It sends no notice to anyone;
telling people is a separate step.

publish and succeed only report unless --apply is given. Each one checks the
state first and refuses if its step is already done or an earlier step is not,
so the order is enforced and a second run changes nothing.
"""
import hashlib
import os
import zipfile
from io import BytesIO, StringIO

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.html import escape
from pyepub import EPUB

from regluit.core.models import Campaign, CampaignAction, Ebook, EbookFile
from regluit.core.models.bibmodels import path_for_file
from regluit.core.parameters import BUY2UNGLUE

# campaign id -> the work it must belong to. Both ids are checked, so a typo in
# the campaign number cannot land on some other book.
ALLOWED = {126: 128685, 137: 137647}

PROVIDER = 'Unglue.it'
LICENSE_PAGE_NAME = 'cc_license.xhtml'

# The app's own page (epub/cc_license.xhtml) reads "After <free-date>, this book
# is released ...", which would print a date decades away for these two. This
# one states the license with no date.
LICENSE_PAGE = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
<title>License Information</title>
</head>
<body>
<div class="booksection">
<p>&#x00A0;</p>
<p class="copyk">This book is released under a %(name)s license. These terms replace and supersede any previous restricted license terms. <a href="%(url)s">%(url)s</a></p>
</div>
</body>
</html>
"""


# Wording on a book's own pages that contradicts the license, replaced when the
# copy is built. campaign id -> [(file inside the epub, the exact text there
# now, what replaces it)]. The replacement may use %(name)s and %(url)s for the
# license. The text must be found exactly once or nothing is built. Only this
# text changes: the copyright notices around it are left as they are.
PAGE_EDITS = {
    126: [(
        'OEBPS/Text/copyright.html',
        'All rights reserved. No part of this publication may be reproduced, stored in a '
        'retrieval system or transmitted, in any form or by any means, electronic, '
        'electrostatic, magnetic tape, mechanical, photocopying, recording or otherwise, '
        'without the prior written permission of the Publisher.',
        'Some rights reserved. This book is released under a %(name)s license: '
        '<a href="%(url)s">%(url)s</a>',
    )],
}


def sha256_of(data):
    return hashlib.sha256(data).hexdigest()


def rights_lines(data):
    """the dc:rights values inside an epub, as a reader's software would see them"""
    book = EPUB(BytesIO(data))
    return [el.text for el in book.opf.iter() if el.tag.endswith('}rights')]


def recompress(epub_bytes, replace=None):
    """The same epub with its entries compressed. The epub library writes every
    entry uncompressed, which made one of the two books 77% larger. The
    mimetype entry stays first and uncompressed, as the format requires.

    replace: {name: bytes} for entries whose contents are to be swapped."""
    replace = replace or {}
    source = zipfile.ZipFile(BytesIO(epub_bytes))
    out = BytesIO()
    with zipfile.ZipFile(out, 'w') as packed:
        packed.writestr('mimetype', source.read('mimetype'), compress_type=zipfile.ZIP_STORED)
        for name in source.namelist():
            if name != 'mimetype':
                packed.writestr(name, replace.get(name, source.read(name)),
                                compress_type=zipfile.ZIP_DEFLATED)
    return out.getvalue()


def edited_pages(original_bytes, campaign):
    """{file name: its new contents} for this campaign's PAGE_EDITS. Raises
    ValueError unless each text to be replaced is found exactly once."""
    license = {
        'name': escape(campaign.get_license_display()),
        'url': escape(campaign.license_url),
    }
    source = zipfile.ZipFile(BytesIO(original_bytes))
    pages = {}
    for name, old, new in PAGE_EDITS.get(campaign.id, []):
        if name not in source.namelist():
            raise ValueError("%s is not in the book" % name)
        text = pages.get(name, source.read(name)).decode('utf-8')
        if text.count(old) != 1:
            raise ValueError("the text to replace was found %s times in %s, expected once" % (
                text.count(old), name))
        pages[name] = text.replace(old, new % license).encode('utf-8')
    return pages


def add_license_page(original_bytes, campaign):
    """Return (new epub as bytes, the rights lines it replaced, the files the
    epub library rewrote, the pages edited as {name: new contents}): the
    original plus a license page, with the campaign's license as its only
    rights line, and with this campaign's PAGE_EDITS applied.

    The epub library writes back onto the file it was opened from when it is
    closed. It is given a copy in memory, never the stored file, so the stored
    original cannot be touched from here."""
    pages = edited_pages(original_bytes, campaign)
    book = EPUB(BytesIO(original_bytes), "a")
    page = LICENSE_PAGE % {
        'name': escape(campaign.get_license_display()),
        'url': escape(campaign.license_url),
    }
    book.addpart(StringIO(page), LICENSE_PAGE_NAME, "application/xhtml+xml", 1)  # after the title, we hope
    # An earlier rights line ("All rights reserved") would contradict the new
    # one, so it is replaced, not added to.
    metadata = book.opf[0]
    replaced = []
    for element in [el for el in metadata if str(el.tag).endswith('}rights')]:
        replaced.append(element.text)
        metadata.remove(element)
    book.info["metadata"].pop('rights', None)
    book.addmetadata('rights', campaign.license_url)
    out = BytesIO()
    book.writetodisk(out)
    # the three files the library always writes afresh (see its _write_epub_zip)
    rewritten = {'META-INF/container.xml', book.opf_path, book.ncx_path}
    return recompress(out.getvalue(), replace=pages), replaced, rewritten, pages


class Command(BaseCommand):
    help = ("Close out a Buy-to-Unglue campaign (126 or 137) step by step: look, build-epub, "
            "publish, succeed. Nothing in the database changes without --apply.")

    def add_arguments(self, parser):
        steps = parser.add_subparsers(dest='step')
        steps.required = True

        look = steps.add_parser('look', help="report the campaign's state; changes nothing")
        look.add_argument('campaign', type=int)
        look.add_argument(
            '--hashes', action='store_true', default=False,
            help="also read each stored epub and print its SHA-256")

        build = steps.add_parser(
            'build-epub', help="write a CC-licensed copy of the stored original to a local file")
        build.add_argument('campaign', type=int)
        build.add_argument('--out', required=True, help="local path to write; must not exist yet")

        publish = steps.add_parser(
            'publish', help="store the approved epub and create the public ebook record")
        publish.add_argument('campaign', type=int)
        publish.add_argument('--epub', required=True, help="the approved epub, a local file")
        publish.add_argument('--sha256', required=True, help="the approved file's SHA-256")
        publish.add_argument('--apply', action='store_true', default=False)

        succeed = steps.add_parser('succeed', help="mark the campaign successful; sends no notice")
        succeed.add_argument('campaign', type=int)
        succeed.add_argument('--apply', action='store_true', default=False)

    def handle(self, *args, **options):
        campaign = self.get_campaign(options['campaign'])
        step = options['step']
        if step == 'look':
            self.look(campaign, options['hashes'])
        elif step == 'build-epub':
            self.build_epub(campaign, options['out'])
        elif step == 'publish':
            self.publish(campaign, options['epub'], options['sha256'], options['apply'])
        elif step == 'succeed':
            self.succeed(campaign, options['apply'])

    def say(self, text=''):
        self.stdout.write(text)

    # ---- reading the state -------------------------------------------------

    def get_campaign(self, campaign_id, lock=False):
        if campaign_id not in ALLOWED:
            raise CommandError("campaign %s is not on the list (%s)" % (
                campaign_id, ", ".join(str(c) for c in sorted(ALLOWED))))
        campaigns = Campaign.objects.select_for_update() if lock else Campaign.objects
        try:
            campaign = campaigns.get(pk=campaign_id)
        except Campaign.DoesNotExist:
            raise CommandError("campaign %s does not exist here" % campaign_id)
        if campaign.work_id != ALLOWED[campaign_id]:
            raise CommandError("campaign %s belongs to work %s, expected %s" % (
                campaign_id, campaign.work_id, ALLOWED[campaign_id]))
        if campaign.type != BUY2UNGLUE:
            raise CommandError("campaign %s is not a Buy-to-Unglue campaign" % campaign_id)
        return campaign

    @staticmethod
    def stored_epubs(campaign):
        """stored epub files on the book, oldest first"""
        return list(EbookFile.objects.filter(
            edition__work_id=campaign.work_id, format='epub',
        ).exclude(file='').order_by('created', 'id'))

    @staticmethod
    def records(campaign):
        """every ebook record on the book, active or not"""
        return list(Ebook.objects.filter(edition__work_id=campaign.work_id).order_by('id'))

    def published(self, campaign):
        """(record, stored file) for the free copy this command publishes, or None.

        That is: an active Unglue.it record carrying the campaign's license,
        whose address is the address of a stored epub linked to it."""
        for ebook in self.records(campaign):
            if not (ebook.active and ebook.provider == PROVIDER and ebook.format == 'epub'
                    and ebook.rights == campaign.license):
                continue
            for ebf in ebook.ebook_files.filter(format='epub').exclude(file='').order_by('id'):
                if ebf.file.url == ebook.url:
                    return ebook, ebf
        return None

    @staticmethod
    def succeeded_records(campaign):
        return list(campaign.actions.filter(type='succeeded').order_by('id'))

    def original_or_refuse(self, campaign):
        """The single stored epub the book was sold from. Refuses unless there is
        exactly one stored epub and it is not linked to a public record."""
        stored = self.stored_epubs(campaign)
        if len(stored) != 1:
            raise CommandError(
                "expected exactly one stored epub on work %s, found %s (%s); look first" % (
                    campaign.work_id, len(stored), ", ".join(str(f.id) for f in stored) or "none"))
        if stored[0].ebook_id is not None:
            raise CommandError("stored epub %s is already linked to ebook record %s" % (
                stored[0].id, stored[0].ebook_id))
        return stored[0]

    @staticmethod
    def read_stored(ebf):
        ebf.file.open('rb')
        try:
            return ebf.file.read()
        finally:
            ebf.file.close()

    # ---- look --------------------------------------------------------------

    def look(self, campaign, hashes=False):
        work = campaign.work
        stored = self.stored_epubs(campaign)
        records = self.records(campaign)
        succeeded = self.succeeded_records(campaign)
        published = self.published(campaign)

        self.say("Campaign %s: %s (work %s)" % (campaign.id, work.title, work.id))
        self.say("  status            %s" % campaign.status)
        self.say("  license           %s" % campaign.license)
        self.say("  target            %s" % campaign.target)
        self.say("  launched          %s" % campaign.activated)
        self.say("  free-date at launch %s" % campaign.cc_date_initial)
        self.say("  rate per day      %s" % campaign.dollar_per_day)
        self.say("  sales counted     %s" % campaign.current_total)
        self.say("  free-date now     %s" % campaign.cc_date)
        self.say("  book marked free  %s" % ("yes" if work.is_free else "no"))

        self.say("  stored epubs (oldest first): %s" % (len(stored) or "none"))
        for ebf in stored:
            line = "    file %s, stored %s, %s, %s" % (
                ebf.id, ebf.created, ebf.file.name,
                "linked to record %s" % ebf.ebook_id if ebf.ebook_id else "not linked to a record")
            if hashes:
                line += ", sha256 %s" % sha256_of(self.read_stored(ebf))
            self.say(line)

        self.say("  ebook records: %s" % (len(records) or "none"))
        for ebook in records:
            self.say("    record %s, %s, %s, %s, %s, %s" % (
                ebook.id, "active" if ebook.active else "inactive", ebook.format,
                ebook.provider, ebook.rights, ebook.url))

        self.say("  'succeeded' records: %s" % (len(succeeded) or "none"))
        for action in succeeded:
            self.say("    action %s, %s" % (action.id, action.timestamp))

        # Acq.get_watermarked() builds a buyer's copy from work.epubfiles()[0],
        # the newest stored epub.
        self.say("  buyers' copies are built from: %s" % (
            "file %s (the newest stored epub)" % stored[-1].id if stored else "nothing stored"))

        staff = User.objects.filter(is_staff=True).count()
        open_supporters = len(campaign.supporters())
        self.say("  a success notice would go to: %s staff, %s users with a still-open transaction" % (
            staff, open_supporters))

        unlinked = [f for f in stored if f.ebook_id is None]
        checks = [
            ("campaign is SUCCESSFUL", campaign.status == 'SUCCESSFUL'),
            ("exactly one 'succeeded' record", len(succeeded) == 1),
            ("the original stored epub is still there, not linked to a record", len(unlinked) == 1),
            ("one active %s record (%s) pointing straight at its stored file" % (
                PROVIDER, campaign.license), published is not None),
            ("no other active ebook records",
             published is not None and [r.id for r in records if r.active] == [published[0].id]),
            ("book is marked free", bool(work.is_free)),
        ]
        self.say()
        self.say("End state:")
        for label, ok in checks:
            self.say("  [%s] %s" % ("yes" if ok else "no ", label))
        self.say("%s of %s end-state checks hold. Nothing was changed." % (
            sum(1 for _, ok in checks if ok), len(checks)))

    # ---- build-epub --------------------------------------------------------

    def build_epub(self, campaign, out_path):
        if os.path.exists(out_path):
            raise CommandError("%s already exists; choose a new name" % out_path)
        original = self.original_or_refuse(campaign)
        original_bytes = self.read_stored(original)
        try:
            licensed, replaced, rewritten, pages = add_license_page(original_bytes, campaign)
        except ValueError as e:
            raise CommandError("not building: %s; nothing written" % e)

        # read the result back before calling it good
        result = zipfile.ZipFile(BytesIO(licensed))
        if result.testzip() is not None:
            raise CommandError("the result is not a sound zip file; nothing written")
        names = result.namelist()
        if not any(name.endswith(LICENSE_PAGE_NAME) for name in names):
            raise CommandError("the license page is missing from the result; nothing written")
        # Nothing from the original may be lost or altered. The exceptions are
        # exactly the three files the epub library writes afresh (the container,
        # the package file, which gains the page and the rights line, and the
        # contents file) and the pages named in PAGE_EDITS, which must come out
        # as exactly the edited text.
        source = zipfile.ZipFile(BytesIO(original_bytes))
        for name in source.namelist():
            if name in rewritten:
                continue
            expected = pages.get(name, source.read(name))
            if name not in names or result.read(name) != expected:
                raise CommandError("%s differs from the original; nothing written" % name)
        if rights_lines(licensed) != [campaign.license_url]:
            raise CommandError("the result's rights lines are not as expected; nothing written")

        with open(out_path, 'xb') as out:
            out.write(licensed)

        self.say("Campaign %s: %s (work %s)" % (campaign.id, campaign.work.title, campaign.work_id))
        self.say("  from stored file %s (%s), %s bytes, sha256 %s" % (
            original.id, original.file.name, len(original_bytes), sha256_of(original_bytes)))
        self.say("  wrote %s, %s bytes" % (out_path, len(licensed)))
        self.say("  sha256 %s" % sha256_of(licensed))
        self.say("  license page added: %s (%s)" % (LICENSE_PAGE_NAME, campaign.get_license_display()))
        self.say("  rights line in the book: %s" % campaign.license_url)
        self.say("  rights lines it replaced: %s" % ("; ".join(str(r) for r in replaced) or "none"))
        for name, old, new in PAGE_EDITS.get(campaign.id, []):
            self.say("  page edited: %s" % name)
            self.say("    was: %s" % old)
            self.say("    now: %s" % (new % {
                'name': campaign.get_license_display(), 'url': campaign.license_url}))
        self.say("  pages of the book edited: %s" % (", ".join(sorted(pages)) or "none"))
        self.say("  apart from those and the container, package and contents files, every file "
                 "in the book is byte-for-byte the original's")
        self.say("The stored original was only read. Nothing in the database or in storage changed.")
        self.say("Next: have the file checked, then run publish with --epub and this --sha256.")

    # ---- publish -----------------------------------------------------------

    def publish_refusal(self, campaign):
        """why publish must not run now, or None"""
        if campaign.status != 'ACTIVE':
            return "campaign status is %s, expected ACTIVE" % campaign.status
        if self.published(campaign):
            return "already published: ebook record %s" % self.published(campaign)[0].id
        active = [r.id for r in self.records(campaign) if r.active]
        if active:
            return "the book already has active ebook records (%s); look first" % ", ".join(
                str(r) for r in active)
        return None

    def publish(self, campaign, epub_path, sha256, apply_changes):
        try:
            with open(epub_path, 'rb') as epub_file:
                data = epub_file.read()
        except OSError as e:
            raise CommandError("could not read %s: %s" % (epub_path, e))
        actual = sha256_of(data)
        if actual != sha256.strip().lower():
            raise CommandError(
                "%s has sha256 %s, not the one given; this is not the approved file" % (
                    epub_path, actual))
        try:
            rights = rights_lines(data)
        except Exception as e:
            raise CommandError("%s does not open as an epub: %s" % (epub_path, e))

        # The record will say the book carries the campaign's license. Only
        # publish a file that says so itself.
        if campaign.license_url not in rights:
            raise CommandError(
                "not publishing: %s has no rights line naming the campaign's license (%s); "
                "its rights lines are: %s" % (
                    epub_path, campaign.license_url, "; ".join(str(r) for r in rights) or "none"))

        refusal = self.publish_refusal(campaign)
        if refusal:
            raise CommandError("not publishing: %s" % refusal)
        original = self.original_or_refuse(campaign)

        self.say("Campaign %s: %s (work %s)" % (campaign.id, campaign.work.title, campaign.work_id))
        self.say("  file %s, %s bytes, sha256 %s" % (epub_path, len(data), actual))
        self.say("  rights lines in the file: %s" % ("; ".join(str(r) for r in rights) or "none"))
        self.say("  edition %s (the edition of the stored original, file %s)" % (
            original.edition_id, original.id))

        if not apply_changes:
            self.say("WOULD store the file beside the original and create one active %s record "
                     "(%s) pointing at it. The book would then be marked free." % (
                         PROVIDER, campaign.license))
            self.say("Nothing changed; run with --apply to change.")
            return

        stored_name = None
        try:
            with transaction.atomic():
                # lock the campaign row and look again, so two runs cannot both publish
                campaign = self.get_campaign(campaign.id, lock=True)
                refusal = self.publish_refusal(campaign)
                if refusal:
                    raise CommandError("not publishing: %s" % refusal)
                original = self.original_or_refuse(campaign)

                ebf = EbookFile(edition=original.edition, format='epub')
                # storage first, and its name noted before any row is written, so
                # that a failure after this point can always name the leftover file
                ebf.file.save(path_for_file(ebf, None), ContentFile(data), save=False)
                stored_name = ebf.file.name
                ebf.save()
                # The address is the stored file's own address. The old indirect
                # /work/<id>/unglued/<format>/ address is what broke in #1283.
                ebook = Ebook.objects.create(
                    edition=original.edition, format='epub', rights=campaign.license,
                    provider=PROVIDER, url=ebf.file.url, filesize=len(data), active=True)
                ebf.ebook = ebook
                ebf.save()

                work = campaign.work
                work.refresh_from_db()
                if not work.is_free:
                    raise CommandError("the book was not marked free after the record was saved")
        except Exception:
            if stored_name:
                # the database rolled back; the uploaded file did not
                self.say("NOT PUBLISHED. Nothing changed in the database. A file was left in "
                         "storage and is not referenced by anything: %s" % stored_name)
            raise

        self.say("PUBLISHED. Created stored file %s (%s) and ebook record %s." % (
            ebf.id, ebf.file.name, ebook.id))
        self.say("  address: %s" % ebook.url)
        self.say("  the book is now marked free")
        self.say("To put it back: deactivate ebook record %s in the admin (the book stops being "
                 "free), then delete stored file %s." % (ebook.id, ebf.id))

    # ---- succeed -----------------------------------------------------------

    def succeed_refusal(self, campaign):
        """why succeed must not run now, or None"""
        if campaign.status != 'ACTIVE':
            return "campaign status is %s, expected ACTIVE" % campaign.status
        if self.succeeded_records(campaign):
            return "the campaign already has a 'succeeded' record"
        published = self.published(campaign)
        if not published:
            return "the free copy is not published yet; run publish first"
        active = [r.id for r in self.records(campaign) if r.active]
        if active != [published[0].id]:
            return "the book has other active ebook records (%s); look first" % ", ".join(
                str(r) for r in active)
        stored = self.stored_epubs(campaign)
        unlinked = [f for f in stored if f.ebook_id is None]
        if len(stored) != 2 or len(unlinked) != 1:
            return ("expected two stored epubs, the original and the published copy; found %s, "
                    "%s of them not linked to a record; look first" % (len(stored), len(unlinked)))
        if not campaign.work.is_free:
            return "the book is not marked free"
        return None

    def succeed(self, campaign, apply_changes):
        refusal = self.succeed_refusal(campaign)
        if refusal:
            raise CommandError("not marking successful: %s" % refusal)

        self.say("Campaign %s: %s (work %s)" % (campaign.id, campaign.work.title, campaign.work_id))

        if not apply_changes:
            self.say("WOULD set the status to SUCCESSFUL and write one 'succeeded' record. "
                     "No notice is sent. Target, dates and rate stay as they are.")
            self.say("Nothing changed; run with --apply to change.")
            return

        with transaction.atomic():
            campaign = self.get_campaign(campaign.id, lock=True)
            refusal = self.succeed_refusal(campaign)
            if refusal:
                raise CommandError("not marking successful: %s" % refusal)
            # update() and not save(): only the status changes
            written = Campaign.objects.filter(pk=campaign.pk, status='ACTIVE').update(status='SUCCESSFUL')
            if written != 1:
                raise CommandError("the campaign changed after it was read; nothing written")
            # same record update_status() writes
            action = CampaignAction.objects.create(
                campaign=campaign, type='succeeded', comment=campaign.current_total)

        self.say("SUCCESSFUL. Wrote 'succeeded' record %s. No notice was sent." % action.id)
        self.say("To put it back: set the status to ACTIVE in the admin and delete campaign "
                 "action %s." % action.id)
