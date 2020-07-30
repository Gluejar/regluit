from django.core.management.base import BaseCommand

from regluit.core.models import EbookFile

removes = [
"https://www.nomos-elibrary.de/10.5771/9783845204512/bildschirmmedien-im-alltag-von-kindern-und-jugendlichen",
"https://www.nomos-elibrary.de/10.5771/9783845204512",
"https://www.nomos-elibrary.de/10.5771/9783845223308",
"https://www.nomos-elibrary.de/10.5771/9783845223339",
"https://www.nomos-elibrary.de/10.5771/9783845223513/die-alterssicherung-von-beamten-und-ihre-reformen-im-rechtsvergleich",
"https://www.nomos-elibrary.de/10.5771/9783845223513",
"https://www.nomos-elibrary.de/10.5771/9783845223926",
"https://www.nomos-elibrary.de/10.5771/9783845224213",
"https://www.nomos-elibrary.de/10.5771/9783845229041",
"https://www.nomos-elibrary.de/10.5771/9783845230368",
"https://www.nomos-elibrary.de/10.5771/9783845231358",
"https://www.nomos-elibrary.de/10.5771/9783845233604",
"https://www.nomos-elibrary.de/10.5771/9783845235059",
"https://www.nomos-elibrary.de/10.5771/9783845235127",
"https://www.nomos-elibrary.de/10.5771/9783845236902/dick-dumm-abhaengig-gewalttaetig?",
"https://www.nomos-elibrary.de/10.5771/9783845236902",
"https://www.nomos-elibrary.de/10.5771/9783845241517",
"https://www.nomos-elibrary.de/10.5771/9783845241760",
"https://www.nomos-elibrary.de/10.5771/9783845242415",
"https://www.nomos-elibrary.de/10.5771/9783845242774",
"https://www.nomos-elibrary.de/10.5771/9783845245881",
"https://www.nomos-elibrary.de/10.5771/9783845246956",
"https://www.nomos-elibrary.de/10.5771/9783845248424",
"https://www.nomos-elibrary.de/10.5771/9783845254555",
"https://www.nomos-elibrary.de/10.5771/9783845255910",
"https://www.nomos-elibrary.de/10.5771/9783845256467/community-collective-marks-status-scope-and-rivals-in-the-european-signs-landscape",
"https://www.nomos-elibrary.de/10.5771/9783845258560/die-krise-der-jungen",
"https://www.nomos-elibrary.de/10.5771/9783845258560",
"https://www.nomos-elibrary.de/10.5771/9783845259390",
"https://www.nomos-elibrary.de/10.5771/9783845261430",
"https://www.nomos-elibrary.de/10.5771/9783845265490",
"https://www.nomos-elibrary.de/10.5771/9783845266534",
"https://www.nomos-elibrary.de/10.5771/9783845273679",
"https://www.nomos-elibrary.de/10.5771/9783845273945",
"https://www.nomos-elibrary.de/10.5771/9783845274072",
"https://www.nomos-elibrary.de/10.5771/9783845279695",
"https://www.nomos-elibrary.de/10.5771/9783845282251",
]

class Command(BaseCommand):

    def handle(self, **options):
        for remove in removes:
            for ebf in EbookFile.objects.filter(source=remove):
                self.stdout.write('removing ebf %s' % ebf.id)
                ebook = ebf.ebook
                ebf.file.delete()
                ebf.delete()
                ebook.delete()