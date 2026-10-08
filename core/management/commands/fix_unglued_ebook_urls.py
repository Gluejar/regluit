"""
Repair ebook records that still point at the removed /work/<id>/unglued/<format>/
address (Gluejar/regluit#1283).

Books freed by a Buy-to-Unglue campaign got a public Ebook record whose url was
that address on our own site. A view answered it by redirecting to the newest
stored file of that format for the book. The view and its route were removed in
9df43685 (2026-02), so download_ebook now redirects readers to a 404.

This points each such record straight at the stored file, which is what newer
records already do.

By default it only reports. Nothing is changed without --apply.
"""
import re

from django.core.management.base import BaseCommand

from regluit.core.models import Ebook, EbookFile

# the removed route: ^work/(?P<work_id>\d+)/unglued/(?P<format>\w+)/$
OLD_ADDRESS = re.compile(r'^https?://[^/]+/work/\d+/unglued/\w+/$')


class Command(BaseCommand):
    help = ("Point active ebook records that use the removed /work/<id>/unglued/<format>/ "
            "address at their stored file. Reports only, unless --apply is given.")

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply', action='store_true', default=False,
            help="change the records; without it the command only reports")

    def handle(self, *args, **options):
        apply_changes = options['apply']
        fixed = skipped = 0
        candidates = Ebook.objects.filter(active=True, url__contains='/unglued/').order_by('id')
        for ebook in candidates:
            if not OLD_ADDRESS.match(ebook.url):
                continue
            work = ebook.edition.work
            label = "ebook %s (work %s, %s)" % (ebook.id, work.id, ebook.format)

            # The removed view served the newest stored file of this format for
            # the book. Only repoint when that file is also the one linked to
            # this record; anything else needs a person to look.
            newest = EbookFile.objects.filter(
                edition__work=work, format=ebook.format,
            ).exclude(file='').order_by('-created', '-id').first()
            if newest is None:
                self.stdout.write("SKIP %s: no stored file of this format" % label)
                skipped += 1
                continue
            if newest.ebook_id != ebook.id:
                self.stdout.write(
                    "SKIP %s: newest stored file %s is not linked to this record"
                    % (label, newest.id))
                skipped += 1
                continue

            new_url = newest.file.url
            # the old address is printed so that the change can be put back by hand
            self.stdout.write("%s %s: %s -> %s (file %s)" % (
                "FIXED" if apply_changes else "WOULD FIX", label, ebook.url, new_url, newest.id))
            if apply_changes:
                # update() and not save(): only the address changes, and no
                # signals or other fields are touched
                Ebook.objects.filter(pk=ebook.pk).update(url=new_url)
            fixed += 1

        self.stdout.write("%s %s, skipped %s%s" % (
            "fixed" if apply_changes else "would fix", fixed, skipped,
            "" if apply_changes else " (nothing changed; run with --apply to change)"))
