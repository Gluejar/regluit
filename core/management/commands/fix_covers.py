from django.core.management.base import BaseCommand

import re
import requests
from regluit.core.models import Edition
from regluit.core.loaders.doab import store_doab_cover

to_fix = [
"20.500.12854/32749",
"20.500.12854/34026",
"20.500.12854/35312",
"20.500.12854/36863",
"20.500.12854/37217",
"20.500.12854/37380",
"20.500.12854/39778",
"20.500.12854/47367",
"20.500.12854/58243",
"20.500.12854/58486",
"20.500.12854/58634",
"20.500.12854/76719",
]
missing = [
"http://opentextbc.ca/anatomyandphysiology/wp-content/plugins/pressbooks/assets/images/default-book-cover.jpg",
"https://ecampusontario.pressbooks.pub/app/uploads/sites/1639/2021/11/social-media-gf08bf90ef_1920-1-350x408.png",
"https://ecampusontario.pressbooks.pub/app/uploads/sites/1659/2021/11/VLS_Book_Cover-1-350x467.png",
"https://ecampusontario.pressbooks.pub/app/uploads/sites/1884/2021/08/HRM-Canadian-edition-book-cover-resized-350x525.jpg",
"https://neuroscience.openetext.utoronto.ca/wp-content/uploads/sites/11/2018/04/FrontCoverFinal.jpg",
"https://oer.ed-beck.com/clone/wp-content/uploads/sites/29/2018/07/Crowd_outside_nyse.jpg",
"https://open.lib.umn.edu/mediaandculture/wp-content/uploads/sites/9/2016/04/Open_Textbook_Library-2.png",
"https://open.lib.umn.edu/organizationalbehavior/wp-content/uploads/sites/197/2017/07/OrgBehav.png",
"https://openbooks.lib.msu.edu/app/uploads/sites/15/2021/04/Elementary-Arabic-Cover-350x525.jpg",
"https://openbooks.lib.msu.edu/app/uploads/sites/65/2021/09/Beginner-Arabic-350x525.jpg",
"https://opentext.wsu.edu/carriecuttler/wp-content/uploads/sites/21/2017/08/RM-Book-Cover-3rd.jpg",
"https://opentextbc.ca/abealfreader6/wp-content/uploads/sites/93/2015/09/BCREADS-COVERS-READER6.jpg",
"https://opentextbc.ca/anatomyandphysiology/wp-content/plugins/pressbooks/assets/images/default-book-cover.jpg",
"https://opentextbc.ca/biology/wp-content/uploads/sites/96/2015/04/Concepts-of-Biology-1st-Canadian-Edition-COVER-STORE.jpg",
"https://opentextbc.ca/geography/wp-content/uploads/sites/34/2014/06/GeographyCover.jpg",
"https://opentextbc.ca/geology/wp-content/uploads/sites/110/2015/09/OTB-Physical-Geology-COVER-STORE.jpg",
"https://opentextbc.ca/indigenizationcurriculumdevelopers/wp-content/uploads/sites/221/2018/07/2-Curriculum-Developers-Version-3.jpg",
"https://opentextbc.ca/indigenizationfoundations/wp-content/uploads/sites/220/2018/08/3-Foundations-Version-4_z.jpg",
"https://opentextbc.ca/indigenizationfrontlineworkers/wp-content/uploads/sites/237/2018/07/5-Front-Line-Advisors-Student-Services-Version-3.jpg",
"https://opentextbc.ca/indigenizationinstructors/wp-content/uploads/sites/238/2018/07/6-Teachers-Instructors-Version-4.jpg",
"https://opentextbc.ca/introductiontopsychology/wp-content/uploads/sites/9/2014/10/IntroToPsych_cover_PBsize.jpg",
"https://opentextbc.ca/introductorychemistry/wp-content/uploads/sites/17/2016/01/OTB014-02-introductory-chemistry-STORE-1.jpg",
"https://opentextbc.ca/principlesofeconomics/wp-content/uploads/sites/149/2016/06/CoverImage.png",
"https://opentextbc.ca/researchmethods/wp-content/uploads/sites/37/2015/10/Research-Methods-2nd-Canadian-Edition-PB-cover1.jpg",
"https://opentextbc.ca/socialpsychology/wp-content/uploads/sites/21/2019/08/OTB025-02-principles-of-social-psychology-1st-international-edition-2018-COVER-STORE.jpg",
"https://opentextbc.ca/wp-content/uploads/sites/360/2021/08/Cover-design-2-350x525.png",
"https://opentextbc.ca/wp-content/uploads/sites/365/2021/10/BookClub-Antiracist-OER-Cover-350x453.jpg",
"https://pressbooks.bccampus.ca/wp-content/uploads/sites/235/2020/09/ASTR1105-solar-scope-generic-350x527.jpg",
"https://pressbooks.bccampus.ca/wp-content/uploads/sites/1141/2021/09/MythoiK-350x544.png",
"https://pressbooks.bccampus.ca/wp-content/uploads/sites/1508/2021/09/TA-bookphoto-350x301.jpg",
"https://pressbooks.nscc.ca/app/uploads/sites/57/2020/06/Open-Education_Pressbooks_Cover-Learning-to-Learn-350x453-1.jpg",
"https://pressbooks.nscc.ca/app/uploads/sites/120/2021/03/Cover-V2-jpg-350x525.jpg",
"https://rc-openlibrary-pb.ecampusontario.ca/introductorychemistry/wp-content/uploads/sites/42/2018/03/Introductory_Chemistry_1st_CDN_Ed_COVER.jpg",
"https://umn.pressbooks.network/app/uploads/sites/192/2017/06/CommRealWorld.png",
"https://uq.pressbooks.pub/app/uploads/sites/13/2021/03/Writing-3_v3.png",
]

class Command(BaseCommand):
    """ To repair covers, will need a new refresh_cover method"""
    help = "fix bad covers"
    
    def add_arguments(self, parser):
        parser.add_argument('doab', nargs='?', default='', help="doab to fix")

    def handle(self, doab, **options):
        if doab == 'mangled':
            self.fix_mangled_covers()
        if doab == 'list':
            for doab_id in to_fix:
                self.fix_doab_cover(doab_id)
            return
        self.fix_doab_cover(doab)

    def fix_doab_cover(self, doab):
        eds = Edition.objects.filter(cover_image__contains=doab)
    
        cover_url = self.refresh_cover(doab)
        if cover_url:
            for e in eds:
                e.cover_image = cover_url
                e.save()
                if e.cover_image_small() and e.cover_image_thumbnail():
                    self.stdout.write('fixed %s  using %s' % (doab, cover_url))
                else:
                    self.stdout.write('bad thumbnails for %s' % cover_url)
                    return False
            return True
        self.stdout.write('removing bad cover for %s' % doab)

        for e in eds:
            e.cover_image = None
            e.save()
        return False

    def fix_mangled_covers(self):
        eds = Edition.objects.filter(cover_image__contains='amazonaws.comdoab')
        for ed in eds:
            cover_url = ed.cover_image.replace('amazonaws.comdoab', 'amazonaws.com/doab')
            ed.cover_image = cover_url
            ed.save()
        self.stdout.write('fixed %s mangled covers' % eds.count())
        eds = Edition.objects.exclude(cover_image__startswith='http').filter(cover_image__regex='.')
        for ed in eds:
            ed.cover_image = ''
            ed.save()
        self.stdout.write('fixed %s file covers' % eds.count())
        fixed = 0
        for cover in missing:
            eds = Edition.objects.filter(cover_image=cover)
            for ed in eds:
                ed.cover_image = ''
                ed.save()
                fixed += 1
        self.stdout.write('fixed %s file covers' % fixed)

    def refresh_cover(self, doab):
        new_cover, created = store_doab_cover(doab, redo=True)
        return new_cover
