from django.core.management.base import BaseCommand
from django.db.models import Count,Subquery, OuterRef, IntegerField

from regluit.core.loaders.doab import get_doab_record
from regluit.core.models import Work, Identifier


class Command(BaseCommand):
    help = "remove duplicate doab ids "

    def handle(self, **options):
        doab_works = Work.objects.annotate(
            doab_count=Subquery(
                Identifier.objects.filter(
                    type='doab',
                    work=OuterRef('pk')
                ).values('work')
                .annotate(cnt=Count('pk'))
                .values('cnt'),
                output_field=IntegerField()
            )
        )
        for w in doab_works.filter(doab_count__gt=1):
            for ident in w.identifiers.filter(type="doab"):
                record = get_doab_record(ident.value)
                if not record:
                    self.stdout.write('removing %s' % ident.value)
                    ident.delete()
