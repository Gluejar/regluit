from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from regluit.core.models import Work

class Command(BaseCommand):
    help = "creates random wishlists for any users"

    def handle(self, *args, **options):
        for user in User.objects.all():
            print user
            try:
                if user.wishlist.works.all().count() != 0:
                    continue
                for work in Work.objects.all():
                    print "adding %s to %s's wishlist" % (work, user)
                    user.wishlist.add_work(work, 'random')
            except Exception, e:
                print e
                pass
