import logging
import math
import re
import urllib
import urllib2
import uuid

from decimal import Decimal
import unicodedata
from urlparse import urlparse

from sorl.thumbnail import get_thumbnail

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import F
from django.db.models.signals import post_save, pre_delete

import regluit
from regluit.marc.models import MARCRecord as NewMARC
from regluit.utils.localdatetime import now
from regluit.questionnaire.models import Landing

from regluit.core import mobi
import regluit.core.cc as cc
from regluit.core.epub import test_epub

from regluit.core.parameters import (
    AGE_LEVEL_CHOICES,
    BORROWED,
    BUY2UNGLUE,
    INDIVIDUAL,
    LIBRARY,
    OFFER_CHOICES,
    TESTING,
    TEXT_RELATION_CHOICES,
    THANKED,
    THANKS,
)

logger = logging.getLogger(__name__)
good_providers = ('Internet Archive', 'Unglue.it', 'Github', 'OAPEN Library')


class Identifier(models.Model):
    # olib, ltwk, goog, gdrd, thng, isbn, oclc, olwk, doab, gute, glue, doi
    type = models.CharField(max_length=4, null=False)
    value = models.CharField(max_length=250, null=False)
    work = models.ForeignKey("Work", related_name="identifiers", null=False)
    edition = models.ForeignKey("Edition", related_name="identifiers", null=True)

    class Meta:
        unique_together = ("type", "value")

    @staticmethod
    def set(type=None, value=None, edition=None, work=None):
        # if there's already an id of this type for this work and edition, change it
        # if not, create it. if the id exists and points to something else, change it.
        identifier = Identifier.get_or_add(type=type, value=value, edition=edition, work=work)
        if identifier.work.id != work.id:
            identifier.work = work
            identifier.save()
        if identifier.edition and edition:
            if identifier.edition.id != edition.id:
                identifier.edition = edition
                identifier.save()
            others = Identifier.objects.filter(type=type, work=work, edition=edition).exclude(value=value)
            if others.count() > 0:
                for other in others:
                    other.delete()
        return identifier

    @staticmethod
    def get_or_add(type='goog', value=None, edition=None, work=None):
        try:
            return Identifier.objects.get(type=type, value=value)
        except Identifier.DoesNotExist:
            i = Identifier(type=type, value=value, edition=edition, work=work)
            i.save()
            return i

    def __unicode__(self):
        return u'{0}:{1}'.format(self.type, self.value)

class Work(models.Model):
    created = models.DateTimeField(auto_now_add=True, db_index=True,)
    title = models.CharField(max_length=1000)
    language = models.CharField(max_length=5, default="en", null=False, db_index=True,)
    openlibrary_lookup = models.DateTimeField(null=True, blank=True)
    num_wishes = models.IntegerField(default=0, db_index=True)
    description = models.TextField(default='', null=True, blank=True)
    selected_edition = models.ForeignKey("Edition", related_name='selected_works', null=True)
    # repurposed earliest_publication to actually be publication range
    publication_range = models.CharField(max_length=50, null=True, blank=True)
    featured = models.DateTimeField(null=True, blank=True, db_index=True,)
    is_free = models.BooleanField(default=False)
    landings = GenericRelation(Landing)
    related = models.ManyToManyField('self', symmetrical=False, null=True, through='WorkRelation', related_name='reverse_related')
    age_level = models.CharField(max_length=5, choices=AGE_LEVEL_CHOICES, default='', blank=True) 

    class Meta:
        ordering = ['title']
    def __unicode__(self):
        return self.title

    def __init__(self, *args, **kwargs):
        self._last_campaign = None
        super(Work, self).__init__(*args, **kwargs)

    @property
    def googlebooks_id(self):
        try:
            preferred_id = self.preferred_edition.googlebooks_id
            # note that there should always be a preferred edition
        except AttributeError:
            # this work has no edition.
            return ''
        if preferred_id:
            return preferred_id
        try:
            return self.identifiers.filter(type='goog')[0].value
        except IndexError:
            return ''

    @property
    def googlebooks_url(self):
        if self.googlebooks_id:
            return "http://books.google.com/books?id=%s" % self.googlebooks_id
        else:
            return ''

    @property
    def goodreads_id(self):
        preferred_id = self.preferred_edition.goodreads_id
        if preferred_id:
            return preferred_id
        try:
            return self.identifiers.filter(type='gdrd')[0].value
        except IndexError:
            return ''

    @property
    def goodreads_url(self):
        return "http://www.goodreads.com/book/show/%s" % self.goodreads_id

    @property
    def librarything_id(self):
        try:
            return self.identifiers.filter(type='ltwk')[0].value
        except IndexError:
            return ''

    @property
    def librarything_url(self):
        return "http://www.librarything.com/work/%s" % self.librarything_id

    @property
    def openlibrary_id(self):
        try:
            return self.identifiers.filter(type='olwk')[0].value
        except IndexError:
            return ''

    @property
    def openlibrary_url(self):
        return "http://openlibrary.org" + self.openlibrary_id

    def cover_filetype(self):
        if self.uses_google_cover():
            return 'jpeg'
        else:
            # consider the path only and not the params, query, or fragment
            url = urlparse(self.cover_image_small().lower()).path

            if url.endswith('.png'):
                return 'png'
            elif url.endswith('.gif'):
                return 'gif'
            elif url.endswith('.jpg') or url.endswith('.jpeg'):
                return 'jpeg'
            else:
                return 'image'

    def uses_google_cover(self):
        if self.preferred_edition and self.preferred_edition.cover_image:
            return False
        else:
            return self.googlebooks_id

    def cover_image_large(self):
        if self.preferred_edition and self.preferred_edition.has_cover_image():
            return self.preferred_edition.cover_image_large()
        return "/static/images/generic_cover_larger.png"

    def cover_image_small(self):
        if self.preferred_edition and self.preferred_edition.has_cover_image():
            return self.preferred_edition.cover_image_small()
        return "/static/images/generic_cover_larger.png"

    def cover_image_thumbnail(self):
        try:
            if self.preferred_edition and self.preferred_edition.has_cover_image():
                return self.preferred_edition.cover_image_thumbnail()
        except IndexError:
            pass
        return "/static/images/generic_cover_larger.png"

    def authors(self):
        # assumes that they come out in the same order they go in!
        if self.preferred_edition and self.preferred_edition.authors.all().count() > 0:
            return  self.preferred_edition.authors.all()
        for edition in self.editions.all():
            if edition.authors.all().count() > 0:
                return edition.authors.all()
        return Author.objects.none()

    def relators(self):
        # assumes that they come out in the same order they go in!
        if self.preferred_edition and self.preferred_edition.relators.all().count() > 0:
            return  self.preferred_edition.relators.all()
        for edition in self.editions.all():
            if edition.relators.all().count() > 0:
                return edition.relators.all()
        return Relator.objects.none()

    def author(self):
        # assumes that they come out in the same order they go in!
        if self.relators().count() > 0:
            return self.relators()[0].name
        return ''

    def authors_short(self):
        # assumes that they come out in the same order they go in!
        if self.relators().count() == 1:
            return self.relators()[0].name
        elif self.relators().count() == 2:
            if self.relators()[0].relation == self.relators()[1].relation:
                if self.relators()[0].relation.code == 'aut':
                    return "%s and %s" % (self.relators()[0].author.name, self.relators()[1].author.name)
                else:
                    return "%s and %s, %ss" % (self.relators()[0].author.name, self.relators()[1].author.name, self.relators()[0].relation.name)
            else:
                return "%s (%s) and %s (%s)" % (self.relators()[0].author.name, self.relators()[0].relation.name, self.relators()[1].author.name, self.relators()[1].relation.name)
        elif self.relators().count() > 2:
            auths = self.relators()
            if auths[0].relation.code == 'aut':
                return "%s et al." % auths[0].author.name
            else:
                return "%s et al. (%ss)" % (auths[0].author.name, auths[0].relation.name)
        return ''

    def kindle_safe_title(self):
        """
        Removes accents, keeps letters and numbers, replaces non-Latin characters with "#", and replaces punctuation with "_"
        """
        safe = u''
        nkfd_form = unicodedata.normalize('NFKD', self.title) #unaccent accented letters
        for c in nkfd_form:
            ccat = unicodedata.category(c)
            #print ccat
            if ccat.startswith('L') or  ccat.startswith('N'): # only letters and numbers
                if ord(c) > 127:
                    safe = safe + '#' #a non latin script letter or number
                else:
                    safe = safe + c
            elif not unicodedata.combining(c): #not accents (combining forms)
                safe = safe + '_' #punctuation
        return safe

    def last_campaign(self):
        # stash away the last campaign to prevent repeated lookups
        if hasattr(self, '_last_campaign_'):
            return self._last_campaign_
        try:
            self._last_campaign_ = self.campaigns.order_by('-created')[0]
        except IndexError:
            self._last_campaign_ = None
        return self._last_campaign_

    @property
    def preferred_edition(self):
        if self.selected_edition:
            return self.selected_edition
        if self.last_campaign():
            if self.last_campaign().edition:
                self.selected_edition = self.last_campaign().edition
                self.save()
                return self.last_campaign().edition
        try:
            self.selected_edition = self.editions.all().order_by('-cover_image', '-created')[0] # prefer editions with covers
            self.save()
            return self.selected_edition
        except IndexError:
            #should only happen if there are no editions for the work,
            #which can happen when works are being merged
            try:
                return WasWork.objects.get(was=self.id).work.preferred_edition
            except WasWork.DoesNotExist:
                #should not happen
                logger.warning('work {} has no edition'.format(self.id))
                return None

    def last_campaign_status(self):
        campaign = self.last_campaign()
        if campaign:
            status = campaign.status
        else:
            if self.first_ebook():
                status = "Available"
            else:
                status = "No campaign yet"
        return status

    def percent_unglued(self):
        status = 0
        campaign = self.last_campaign()
        if campaign is not None:
            if campaign.status == 'SUCCESSFUL':
                status = 6
            elif campaign.status == 'ACTIVE':
                if campaign.target is not None:
                    target = float(campaign.target)
                else:
                    #shouldn't happen, but did once because of a failed pdf conversion
                    return 0
                if target <= 0:
                    status = 6
                else:
                    if campaign.type == BUY2UNGLUE:
                        status = int(6 - 6*campaign.left/campaign.target)
                    else:
                        status = int(float(campaign.current_total)*6/target)
                    if status >= 6:
                        status = 6
        return status

    def percent_of_goal(self):
        campaign = self.last_campaign()
        return 0 if campaign is None else campaign.percent_of_goal()

    def ebooks_all(self):
        return self.ebooks(all=True)

    def ebooks(self, all=False):
        if all:
            return Ebook.objects.filter(edition__work=self).order_by('-created')
        else:
            return Ebook.objects.filter(edition__work=self, active=True).order_by('-created')

    def ebookfiles(self):
        return EbookFile.objects.filter(edition__work=self).exclude(file='').order_by('-created')

    def epubfiles(self):
        # filter out non-epub because that's what booxtream accepts
        return EbookFile.objects.filter(edition__work=self, format='epub').exclude(file='').order_by('-created')

    def mobifiles(self):
        return EbookFile.objects.filter(edition__work=self, format='mobi').exclude(file='').order_by('-created')

    def pdffiles(self):
        return EbookFile.objects.filter(edition__work=self, format='pdf').exclude(file='').order_by('-created')
    
    def versions(self):
        version_labels = []
        for ebook in self.ebooks_all():
            if ebook.version_label and not ebook.version_label in version_labels:
                version_labels.append(ebook.version_label)
        return version_labels
    
    def formats(self):
        fmts = []
        for fmt in ['pdf', 'epub', 'mobi', 'html']:
            for ebook in self.ebooks().filter(format=fmt):
                fmts.append(fmt)
                break
        return fmts

    def remove_old_ebooks(self):
        # this method is triggered after an file upload or new ebook saved
        old = Ebook.objects.filter(edition__work=self, active=True).order_by('-version_iter', '-created')
        
        # keep highest version ebook for each format and version label
        done_format_versions = []
        for eb in old:
            format_version = '{}_{}'.format(eb.format, eb.version_label)
            if format_version in done_format_versions:
                eb.deactivate()
            else:
                done_format_versions.append(format_version)
        
        # check for failed uploads.
        null_files = EbookFile.objects.filter(edition__work=self, file='')
        for ebf in null_files:
            ebf.file.delete()
            ebf.delete()

    @property
    def download_count(self):
        dlc = 0
        for ebook in self.ebooks(all=True):
            dlc += ebook.download_count
        return dlc

    def first_pdf(self):
        return self.first_ebook('pdf')

    def first_epub(self):
        return self.first_ebook('epub')

    def first_pdf_url(self):
        try:
            url = self.first_ebook('pdf').url
            return url
        except:
            return None

    def first_epub_url(self):
        try:
            url = self.first_ebook('epub').url
            return url
        except:
            return None

    def first_ebook(self, ebook_format=None):
        if ebook_format:
            for ebook in self.ebooks().filter(format=ebook_format):
                return ebook
        else:
            for ebook in self.ebooks():
                return ebook

    def wished_by(self):
        return User.objects.filter(wishlist__works__in=[self])

    def update_num_wishes(self):
        self.num_wishes = self.wishes.count()
        self.save()

    def priority(self):
        if self.last_campaign():
            return 5
        freedom = 1 if self.is_free else 0
        wishing = int(math.log(self.num_wishes)) + 1 if self.num_wishes else 0
        return min(freedom + wishing, 5)

    def first_oclc(self):
        if self.preferred_edition is None:
            return ''
        preferred_id = self.preferred_edition.oclc
        if preferred_id:
            return preferred_id
        try:
            return self.identifiers.filter(type='oclc')[0].value
        except IndexError:
            return ''

    def first_isbn_13(self):
        if self.preferred_edition is None:
            return ''
        preferred_id = self.preferred_edition.isbn_13
        if preferred_id:
            return preferred_id
        try:
            return self.identifiers.filter(type='isbn')[0].value
        except IndexError:
            return ''

    @property
    def earliest_publication_date(self):
        for edition in Edition.objects.filter(work=self, publication_date__isnull=False).order_by('publication_date'):
            if edition.publication_date and len(edition.publication_date) >= 4:
                return edition.publication_date

    @property
    def publication_date(self):
        if self.publication_range:
            return  self.publication_range
        for edition in Edition.objects.filter(work=self, publication_date__isnull=False).order_by('publication_date'):
            if edition.publication_date:
                try:
                    earliest_publication = edition.publication_date[:4]
                except IndexError:
                    continue
                latest_publication = None
                for edition in Edition.objects.filter(work=self, publication_date__isnull=False).order_by('-publication_date'):
                    if edition.publication_date:
                        try:
                            latest_publication = edition.publication_date[:4]
                        except IndexError:
                            continue
                        break
                if earliest_publication == latest_publication:
                    publication_range = earliest_publication
                else:
                    publication_range = earliest_publication + "-" + latest_publication
                self.publication_range = publication_range
                self.save()
                return publication_range
        return ''

    @property
    def has_unglued_edition(self):
        """
        allows us to distinguish successful campaigns with ebooks still in progress from successful campaigns with ebooks available
        """
        if self.ebooks().filter(edition__unglued=True):
            return True
        return False

    @property
    def user_with_rights(self):
        """
        return queryset of users (should be at most one) who act for rights holders with active claims to the work
        """
        claims = self.claim.filter(status='active')
        assert claims.count() < 2, "There is more than one active claim on %r" % self.title
        try:
            return claims[0].user
        except:
            return False

    def get_absolute_url(self):
        return reverse('work', args=[str(self.id)])

    def publishers(self):
        # returns a set of publishers associated with this Work
        return Publisher.objects.filter(name__editions__work=self).distinct()

    def create_offers(self):
        for choice in OFFER_CHOICES:
            if not self.offers.filter(license=choice[0]):
                self.offers.create(license=choice[0], active=True, price=Decimal(10))
        return self.offers.all()

    def get_lib_license(self, user):
        lib_user = (lib.user for lib in user.profile.libraries)
        return self.get_user_license(lib_user)

    def borrowable(self, user):
        if user.is_anonymous():
            return False
        lib_license = self.get_lib_license(user)
        if lib_license and lib_license.borrowable:
            return True
        return False

    def lib_thanked(self, user):
        if user.is_anonymous():
            return False
        lib_license = self.get_lib_license(user)
        if lib_license and lib_license.thanked:
            return True
        return False

    def in_library(self, user):
        if user.is_anonymous():
            return False
        lib_license = self.get_lib_license(user)
        if lib_license and lib_license.acqs.count():
            return True
        return False

    @property
    def lib_acqs(self):
        return  self.acqs.filter(license=LIBRARY)

    @property
    def test_acqs(self):
        return  self.acqs.filter(license=TESTING).order_by('-created')

    class user_license:
        acqs = Identifier.objects.none() # Identifier is just convenient.
        def __init__(self, acqs):
            self.acqs = acqs

        @property
        def is_active(self):
            return  self.acqs.filter(expires__isnull=True).count() > 0 or self.acqs.filter(expires__gt=now()).count() > 0

        @property
        def borrowed(self):
            loans = self.acqs.filter(license=BORROWED, expires__gt=now())
            if loans.count() == 0:
                return None
            else:
                return loans[0]

        @property
        def purchased(self):
            purchases = self.acqs.filter(license=INDIVIDUAL, expires__isnull=True)
            if purchases.count() == 0:
                return None
            else:
                return purchases[0]

        @property
        def lib_acqs(self):
            return  self.acqs.filter(license=LIBRARY)

        @property
        def next_acq(self):
            """ This is the next available copy in the user's libraries"""
            loans = self.acqs.filter(license=LIBRARY, refreshes__gt=now()).order_by('refreshes')
            if loans.count() == 0:
                return None
            else:
                return loans[0]

        @property
        def borrowable(self):
            return  self.acqs.filter(license=LIBRARY, refreshes__lt=now()).count() > 0

        @property
        def thanked(self):
            return  self.acqs.filter(license=THANKED).count() > 0

        @property
        def borrowable_acq(self):
            for acq in self.acqs.filter(license=LIBRARY, refreshes__lt=now()):
                return acq

        @property
        def is_duplicate(self):
            # does user have two individual licenses?
            pending = self.acqs.filter(license=INDIVIDUAL, expires__isnull=True, gifts__used__isnull=True).count()
            return self.acqs.filter(license=INDIVIDUAL, expires__isnull=True).count() > pending


    def get_user_license(self, user):
        """ This is all the acqs, wrapped in user_license object for the work, user(s) """
        if user is None:
            return None
        if hasattr(user, 'is_anonymous'):
            if user.is_anonymous():
                return None
            return self.user_license(self.acqs.filter(user=user))
        else:
            # assume it's several users
            return self.user_license(self.acqs.filter(user__in=user))

    @property
    def has_marc(self):
        for record in  NewMARC.objects.filter(edition__work=self):
            return True
        return False

    ### for compatibility with MARC output
    def marc_records(self):
        record_list = []
        record_list.extend(NewMARC.objects.filter(edition__work=self))
        for obj in record_list:
            break
        else:
            for ebook in self.ebooks():
                record_list.append(ebook.edition)
                break
        return record_list

class WorkRelation(models.Model):
    to_work = models.ForeignKey('Work', related_name='works_related_to')
    from_work= models.ForeignKey('Work', related_name='works_related_from')
    relation = models.CharField(max_length=15, choices=TEXT_RELATION_CHOICES)


class Author(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255, unique=True)
    editions = models.ManyToManyField("Edition", related_name="authors", through="Relator")

    def __unicode__(self):
        return self.name

    @property
    def last_name_first(self):
        names = self.name.rsplit()
        if len(names) == 0:
            return ''
        elif len(names) == 1:
            return names[0]
        elif len(names) == 2:
            return names[1] + ", " + names[0]
        else:
            reversed_name = names[-1]+","
            for name in names[0:-1]:
                reversed_name += " "
                reversed_name += name
            return reversed_name

class Relation(models.Model):
    code = models.CharField(max_length=3, blank=False, db_index=True, unique=True)
    name = models.CharField(max_length=30, blank=True,)

class Relator(models.Model):
    relation = models.ForeignKey('Relation', default=1) #first relation should have code='aut'
    author = models.ForeignKey('Author')
    edition = models.ForeignKey('Edition', related_name='relators')
    class Meta:
        db_table = 'core_author_editions'

    @property
    def name(self):
        if self.relation.code == 'aut':
            return self.author.name
        else:
            return "%s (%s)" % (self.author.name, self.relation.name)

    def set(self, relation_code):
        if self.relation.code != relation_code:
            try:
                self.relation = Relation.objects.get(code=relation_code)
                self.save()
            except Relation.DoesNotExist:
                logger.warning("relation not found: code = %s" % relation_code)

class Subject(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=200, unique=True)
    works = models.ManyToManyField("Work", related_name="subjects")
    is_visible = models.BooleanField(default=True)
    authority = models.CharField(max_length=10, blank=False, default="")

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name


    @property
    def kw(self):
        return 'kw.%s' % self.name

    def free_works(self):
        return self.works.filter(is_free=True)

class Edition(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=1000)
    publisher_name = models.ForeignKey("PublisherName", related_name="editions", null=True, blank=True)
    publication_date = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    work = models.ForeignKey("Work", related_name="editions", null=True)
    cover_image = models.URLField(null=True, blank=True)
    unglued = models.BooleanField(default=False)
    note = models.ForeignKey("EditionNote", null=True, blank=True)

    def __unicode__(self):
        if self.isbn_13:
            return "%s (ISBN %s) %s" % (self.title, self.isbn_13, self.publisher)
        if self.oclc:
            return "%s (OCLC %s) %s" % (self.title, self.oclc, self.publisher)
        if self.googlebooks_id:
            return "%s (GOOG %s) %s" % (self.title, self.googlebooks_id, self.publisher)
        else:
            return "%s (GLUE %s) %s" % (self.title, self.id, self.publisher)

    def cover_image_large(self):
        #550 pixel high image
        if self.cover_image:
            im = get_thumbnail(self.cover_image, 'x550', crop='noop', quality=95)
            if im.exists():
                return im.url
        elif self.googlebooks_id:
            url = "https://encrypted.google.com/books?id=%s&printsec=frontcover&img=1&zoom=0" % self.googlebooks_id
            im = get_thumbnail(url, 'x550', crop='noop', quality=95)
            if not im.exists() or im.storage.size(im.name) == 16392: # check for "image not available" image
                url = "https://encrypted.google.com/books?id=%s&printsec=frontcover&img=1&zoom=1" % self.googlebooks_id
                im = get_thumbnail(url, 'x550', crop='noop', quality=95)
            if im.exists():
                return im.url
            else:
                return ''
        else:
            return ''

    def cover_image_small(self):
        #80 pixel high image
        if self.cover_image:
            im = get_thumbnail(self.cover_image, 'x80', crop='noop', quality=95)
            if im.exists():
                return im.url
        if self.googlebooks_id:
            return "https://encrypted.google.com/books?id=%s&printsec=frontcover&img=1&zoom=5" % self.googlebooks_id
        else:
            return ''

    def cover_image_thumbnail(self):
        #128 pixel wide image
        if self.cover_image:
            im = get_thumbnail(self.cover_image, '128', crop='noop', quality=95)
            if im.exists():
                return im.url
        if self.googlebooks_id:
            return "https://encrypted.google.com/books?id=%s&printsec=frontcover&img=1&zoom=1" % self.googlebooks_id
        else:
            return ''

    def has_cover_image(self):
        if self.cover_image:
            return self.cover_image
        elif self.googlebooks_id:
            return True
        else:
            return False

    @property
    def publisher(self):
        if self.publisher_name:
            return self.publisher_name.name
        return ''

    @property
    def isbn_10(self):
        return regluit.core.isbn.convert_13_to_10(self.isbn_13)

    def id_for(self, type):
        if not self.pk:
            return ''
        try:
            return self.identifiers.filter(type=type)[0].value
        except IndexError:
            return ''

    @property
    def isbn_13(self):
        return self.id_for('isbn')

    @property
    def googlebooks_id(self):
        return self.id_for('goog')

    @property
    def librarything_id(self):
        return self.id_for('thng')

    @property
    def oclc(self):
        return self.id_for('oclc')

    @property
    def doi(self):
        return self.id_for('doi')

    @property
    def goodreads_id(self):
        return self.id_for('gdrd')

    @property
    def http_id(self):
        return self.id_for('http')

    @staticmethod
    def get_by_isbn(isbn):
        if len(isbn) == 10:
            isbn = regluit.core.isbn.convert_10_to_13(isbn)
        try:
            return Identifier.objects.get(type='isbn', value=isbn).edition
        except Identifier.DoesNotExist:
            return None

    def add_author(self, author_name, relation='aut'):
        if author_name:
            (author, created) = Author.objects.get_or_create(name=author_name)
            (relation, created) = Relation.objects.get_or_create(code=relation)
            (new_relator, created) = Relator.objects.get_or_create(author=author, edition=self)
            if new_relator.relation != relation:
                new_relator.relation = relation
                new_relator.save()

    def remove_author(self, author):
        if author:
            try:
                relator = Relator.objects.get(author=author, edition=self)
                relator.delete()
            except Relator.DoesNotExist:
                pass

    def set_publisher(self, publisher_name):
        if publisher_name and publisher_name != '':
            try:
                pub_name = PublisherName.objects.get(name=publisher_name)
                if pub_name.publisher:
                    pub_name = pub_name.publisher.name
            except PublisherName.DoesNotExist:
                pub_name = PublisherName.objects.create(name=publisher_name)
                pub_name.save()

            self.publisher_name = pub_name
            self.save()

    #### following methods for compatibility with marc outputter
    def downloads(self):
        return self.ebooks.filter(active=True)

    def download_via_url(self):
        return settings.BASE_URL_SECURE + reverse('download', args=[self.work.id])

    def authnames(self):
        return [auth.last_name_first for auth in self.authors.all()]

    @property
    def license(self):
        try:
            return self.ebooks.all()[0].rights
        except:
            return None

    @property
    def funding_info(self):
        if self.ebooks.all().count() == 0:
            return ''
        if self.unglued:
            return 'The book is available as a free download thanks to the generous support of interested readers and organizations, who made donations using the crowd-funding website Unglue.it.'
        else:
            if self.ebooks.all()[0].rights in cc.LICENSE_LIST:
                return 'The book is available as a free download thanks to a Creative Commons license.'
            else:
                return 'The book is available as a free download because it is in the Public Domain.'

    @property
    def description(self):
        return self.work.description

class EditionNote(models.Model):
    note = models.CharField(max_length=64, null=True, blank=True, unique=True)
    def __unicode__(self):
        return self.note

class Publisher(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.ForeignKey('PublisherName', related_name='key_publisher')
    url = models.URLField(max_length=1024, null=True, blank=True)
    logo_url = models.URLField(max_length=1024, null=True, blank=True)
    description = models.TextField(default='', null=True, blank=True)

    def __unicode__(self):
        return self.name.name

class PublisherName(models.Model):
    name = models.CharField(max_length=255, blank=False, unique=True)

    publisher = models.ForeignKey('Publisher', related_name='alternate_names', null=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(PublisherName, self).save(*args, **kwargs) # Call the "real" save() method.
        if self.publisher and self != self.publisher.name:
            #this name is an alias, repoint all editions with this name to the other.
            for edition in Edition.objects.filter(publisher_name=self):
                edition.publisher_name = self.publisher.name
                edition.save()


class WasWork(models.Model):
    work = models.ForeignKey('Work')
    was = models.IntegerField(unique=True)
    moved = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)

def safe_get_work(work_id):
    """
    use this rather than querying the db directly for a work by id
    """
    try:
        work = Work.objects.get(id=work_id)
    except Work.DoesNotExist:
        try:
            work = WasWork.objects.get(was=work_id).work
        except WasWork.DoesNotExist:
            raise Work.DoesNotExist()
    except ValueError:
        #work_id is not a number
        raise Work.DoesNotExist()
    return work

def path_for_file(instance, filename):
    return "ebf/{}.{}".format(uuid.uuid4().get_hex(), instance.format)

class EbookFile(models.Model):
    file = models.FileField(upload_to=path_for_file)
    format = models.CharField(max_length=25, choices=settings.FORMATS)
    edition = models.ForeignKey('Edition', related_name='ebook_files')
    created = models.DateTimeField(auto_now_add=True)
    asking = models.BooleanField(default=False)
    ebook = models.ForeignKey('Ebook', related_name='ebook_files', null=True)
    version = None
    def check_file(self):
        if self.format == 'epub':
            return test_epub(self.file)
        return None

    @property
    def active(self):
        try:
            return Ebook.objects.filter(url=self.file.url)[0].active
        except:
            return False

    def make_mobi(self):
        if not self.format == 'epub':
            return False
        new_mobi_ebf = EbookFile.objects.create(edition=self.edition, format='mobi', asking=self.asking)
        new_mobi_ebf.file.save(path_for_file('ebf', None), ContentFile(mobi.convert_to_mobi(self.file.url)))
        new_mobi_ebf.save()
        if self.ebook:
            new_ebook = Ebook.objects.create(
                edition=self.edition,
                format='mobi',
                url=new_mobi_ebf.file.url,
                rights=self.ebook.rights,
                version_label=self.ebook.version_label,
                version_iter=self.ebook.version_iter,
            )
            new_mobi_ebf.ebook = new_ebook
        new_mobi_ebf.save()
        return True

send_to_kindle_limit = 7492232

class Ebook(models.Model):
    url = models.URLField(max_length=1024) #change to unique?
    created = models.DateTimeField(auto_now_add=True, db_index=True,)
    format = models.CharField(max_length=25, choices=settings.FORMATS)
    provider = models.CharField(max_length=255)
    download_count = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    filesize = models.PositiveIntegerField(null=True)
    version_label = models.CharField(max_length=255, default="", blank=True)
    version_iter = models.PositiveIntegerField(default=0)

    # use 'PD-US', 'CC BY', 'CC BY-NC-SA', 'CC BY-NC-ND', 'CC BY-NC', 'CC BY-ND', 'CC BY-SA', 'CC0'
    rights = models.CharField(max_length=255, null=True, choices=cc.CHOICES, db_index=True)
    edition = models.ForeignKey('Edition', related_name='ebooks')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)

    def kindle_sendable(self):
        if not self.filesize or self.filesize < send_to_kindle_limit:
            return True
        else:
            return False

    def get_archive(self):  # returns an open file
        ebf = self.get_archive_ebf()
        if not ebf:
            return None
        try:
            ebf.file.open()
        except ValueError:
            logger.error(u'couldn\'t open EbookFile {}'.format(ebf.id))
            return None
        except IOError:
            logger.error(u'EbookFile {} does not exist'.format(ebf.id))
            return None
        return ebf.file

    def get_archive_ebf(self): # returns an ebf
        if not self.ebook_files.filter(asking=False):
            if not self.provider in good_providers:
                return None
            try:
                r = urllib2.urlopen(self.url)
                try:
                    self.filesize = int(r.info().getheaders("Content-Length")[0])
                    if self.save:
                        self.filesize = self.filesize if self.filesize < 2147483647 else 2147483647  # largest safe positive integer
                        self.save()
                    ebf = EbookFile.objects.create(edition=self.edition, ebook=self, format=self.format)
                    ebf.file.save(path_for_file(ebf, None), ContentFile(r.read()))
                    ebf.file.close()
                    ebf.save()
                    return ebf
                except IndexError:
                    # response has no Content-Length header probably a bad link
                    logging.error('Bad link error: {}'.format(self.url))
            except IOError:
                logger.error(u'could not open {}'.format(self.url))
        else:
            ebf = self.ebook_files.filter(asking=False).order_by('-created')[0]
            return ebf

    def set_provider(self):
        self.provider = Ebook.infer_provider(self.url)
        return self.provider

    @property
    def version(self):
        if self.version_label is None:
            return '.{}'.format(self.version_iter)
        else:
            return '().{}'.format(self.version_label, self.version_iter)
    
    def set_version(self, version):
        #set both version_label and version_iter with one string with format "version.iter"
        version_pattern = r'(.*)\.(\d+)$'
        match = re.match(version_pattern,version)
        if match:
            (self.version_label, self.version_iter) = (match.group(1), match.group(2))
        else:
            self.version_label = version
        self.save()
        
    def set_next_iter(self):
        # set the version iter to the next unused iter for that version
        for ebook in Ebook.objects.filter(
                    edition=self.edition, 
                    version_label=self.version_label,
                    format=self.format,
                    provider=self.provider
                ).order_by('-version_iter'):
             iter = ebook.version_iter
             break
        self.version_iter = iter + 1
        self.save()
          
    @property
    def rights_badge(self):
        if self.rights is None:
            return cc.CCLicense.badge('PD-US')
        return cc.CCLicense.badge(self.rights)

    @staticmethod
    def infer_provider(url):
        if not url:
            return None
        # provider derived from url. returns provider value. remember to call save() afterward
        if re.match(r'https?://books.google.com/', url):
            provider = 'Google Books'
        elif re.match(r'https?://www.gutenberg.org/', url):
            provider = 'Project Gutenberg'
        elif re.match(r'https?://(www\.|)archive.org/', url):
            provider = 'Internet Archive'
        elif url.startswith('http://hdl.handle.net/2027/') or url.startswith('http://babel.hathitrust.org/'):
            provider = 'Hathitrust'
        elif re.match(r'https?://\w\w\.wikisource\.org/', url):
            provider = 'Wikisource'
        elif re.match(r'https?://\w\w\.wikibooks\.org/', url):
            provider = 'Wikibooks'
        elif re.match(r'https://github\.com/[^/ ]+/[^/ ]+/raw/[^ ]+', url):
            provider = 'Github'
        else:
            provider = None
        return provider

    def increment(self):
        Ebook.objects.filter(id=self.id).update(download_count=F('download_count') +1)

    @property
    def download_url(self):
        return settings.BASE_URL_SECURE + reverse('download_ebook', args=[self.id])

    def is_direct(self):
        return self.provider not in ('Google Books', 'Project Gutenberg')

    def __unicode__(self):
        return "%s (%s from %s)" % (self.edition.title, self.format, self.provider)

    def deactivate(self):
        self.active = False
        self.save()

    def activate(self):
        self.active = True
        self.save()

def set_free_flag(sender, instance, created, **kwargs):
    if created:
        if not instance.edition.work.is_free and instance.active:
            instance.edition.work.is_free = True
            instance.edition.work.save()
    elif not instance.active and instance.edition.work.is_free and instance.edition.work.ebooks().count() == 0:
        instance.edition.work.is_free = False
        instance.edition.work.save()
    elif instance.active and not instance.edition.work.is_free and instance.edition.work.ebooks().count() > 0:
        instance.edition.work.is_free = True
        instance.edition.work.save()

post_save.connect(set_free_flag, sender=Ebook)

def reset_free_flag(sender, instance, **kwargs):
    # if the Work associated with the instance Ebook currenly has only 1 Ebook, then it's no longer a free Work
    # once the instance Ebook is deleted.
    if instance.edition.work.ebooks().count() == 1:
        instance.edition.work.is_free = False
        instance.edition.work.save()

pre_delete.connect(reset_free_flag, sender=Ebook)
