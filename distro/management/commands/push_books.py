from datetime import datetime
from django.core.management.base import BaseCommand
from regluit.distro.models import Target
from regluit.distro.push import push_all, push_books


class Command(BaseCommand):
    help = "ftp <max> books to <target> or 'all' <since> date . "
    args = "<max> <target> <since> <new>"

    def handle(self, max=0, target=None, since=None, new=None, *args, **options):
        try:
            max=int(max)
        except:
            self.stderr.write("max should be number (0 for all available) ")
            return
        new = new=='new'
        if new:
            self.stdout.write(  "previously deposited books will not be pushed")
        try:
            since = datetime.strptime(since, '%Y-%m-%d')
        except:
            since=None

        if since:
            try:
                target = Target.objects.get(name=target)
                self.stdout.write( "pushing {} new books since {} to {}".format(max if max else 'all', since, target))
                push_books(target, max=max, start=since, new=new)
            except Target.DoesNotExist:
                if target == "all":
                    self.stdout.write(  "pushing {} to all targets".format(max if max else 'all'))
                    push_all(start=since, max=max, new=new)
                else:
                    self.stderr.write("'{}' is not a defined target".format(target))
        else:
            try:
                self.stdout.write( "pushing {} books to {}".format(max if max else 'all', target))
                target = Target.objects.get(name=target)
                push_books(target,  max=max, new=new)
            except Target.DoesNotExist:
                if target == "all":
                    self.stdout.write("pushing {} books to all targets".format(max if max else 'all'))
                    push_all(max=max, new=new)
                else:
                    self.stderr.write("'{}' is not a defined target".format(target))

            
