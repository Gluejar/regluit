from django.contrib.sites.models import Site
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Localize the current Site row (SITE_ID) to this box's domain.

    Useful after snapshot-restoring a staging box from prod: the DB will still
    carry prod's Site row, causing emailed links (password-reset, notices, etc.)
    to point at production.  Run this command as a post-deploy step to fix it.

    Idempotent: if the Site row already matches the requested domain/name, it
    prints a "no-op" message and exits cleanly without touching the DB.
    """

    help = "Update the current Site row (SITE_ID) to the given domain and name"

    def add_arguments(self, parser):
        parser.add_argument(
            "domain",
            help="Domain to set on the current Site row (e.g. dj42.unglue.it)",
        )
        parser.add_argument(
            "name",
            nargs="?",
            default=None,
            help="Display name to set on the Site row (defaults to domain if omitted)",
        )

    def handle(self, domain, name, **options):
        site_id = settings.SITE_ID
        display_name = name if name else domain

        # Use get_or_create so a fresh / scrubbed DB without a SITE_ID row is
        # created correctly rather than hard-failing the deploy with
        # Site.DoesNotExist (Codex review 2026-06-16).
        site, created = Site.objects.get_or_create(
            pk=site_id,
            defaults={"domain": domain, "name": display_name},
        )
        if created:
            Site.objects.clear_cache()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Updated Site (pk={site_id}): created with "
                    f"domain={site.domain!r}  name={site.name!r}"
                )
            )
            return

        self.stdout.write(
            f"Current Site (pk={site_id}): domain={site.domain!r}  name={site.name!r}"
        )

        if site.domain == domain and site.name == display_name:
            self.stdout.write("Site row already matches requested values — no-op.")
            return

        site.domain = domain
        site.name = display_name
        site.save()
        # Clear the Sites framework cache so the new value takes effect immediately.
        Site.objects.clear_cache()

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated Site (pk={site_id}): domain={site.domain!r}  name={site.name!r}"
            )
        )
