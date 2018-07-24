'''
views to edit bibmodels
'''
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.urls import reverse
from django.db.models import Q
from django.http import (
    HttpResponseRedirect,
    Http404,
)
from django.shortcuts import render

from regluit.core import models

from regluit.core.bookloader import (
    add_by_googlebooks_id,
    add_by_isbn,
    add_by_oclc,
)
from regluit.core.parameters import WORK_IDENTIFIERS

from regluit.core.loaders import add_by_webpage
from regluit.core.loaders.doab import add_by_doab
from regluit.core.loaders.utils import ids_from_urls
from regluit.frontend.forms import EditionForm, IdentifierForm

from .rh_views import user_is_rh


def user_can_edit_work(user, work):
    '''
    Check if a user is allowed to edit the work
    '''
    if user.is_anonymous:
        return False
    elif user.is_staff :
        return True
    elif work and work.last_campaign():
        return user in work.last_campaign().managers.all()
    elif user_is_rh(user) and (work == None or not work.last_campaign()):
        # allow rights holders to edit unless there is a campaign
        return True
    elif work and work.claim.all():
        return True if work.claim.filter(user=user) else False
    else:
        return user.profile in work.contributors.all()

def safe_get_work(work_id):
    """
    use this rather than querying the db directly for a work by id
    """
    try:
        work = models.safe_get_work(work_id)
    except models.Work.DoesNotExist:
        raise Http404
    return work

def add_subject(subject_name, work, authority=''):
    '''
    add a subject to a work
    '''
    try:
        subject = models.Subject.objects.get(name=subject_name)
    except models.Subject.DoesNotExist:
        subject = models.Subject.objects.create(name=subject_name, authority=authority)
    subject.works.add(work)

def get_edition(edition_id):
    '''
    get edition and 404 if not found
    '''
    try:
        return models.Edition.objects.get(id = edition_id)
    except models.Edition.DoesNotExist:
        raise Http404 (duplicate-code)

def user_edition(edition, user):
    if user and user.is_authenticated and edition:
        user.profile.works.add(edition.work)
    return edition

def get_edition_for_id(id_type, id_value, user=None):
    ''' the identifier is assumed to not be in database '''
    identifiers = {id_type: id_value}
    if id_type == 'http':
        # check for urls implying other identifiers
        identifiers.update(ids_from_urls(id_value))
        for new_id_type in identifiers.keys():
            idents = models.Identifier.objects.filter(
                type=new_id_type,
                value=identifiers[new_id_type],
            )
            if idents:
                ident = idents[0]
                return ident.edition if ident.edition else ident.work.preferred_edition

    #need to make a new edition
    if identifiers.has_key('goog'):
        edition = add_by_googlebooks_id(identifiers['goog'])
        if edition:
            
            return user_edition(edition, user)

    if identifiers.has_key('isbn'):
        edition = add_by_isbn(identifiers['isbn'])
        if edition:
            return user_edition(edition, user)
    
    if identifiers.has_key('doab'):
        edition = add_by_doab(identifiers['doab'])
        if edition:
            return user_edition(edition, user)
    
    if identifiers.has_key('oclc'):
        edition = add_by_oclc(identifiers['oclc'])
        if edition:
            return user_edition(edition, user)
    
    if identifiers.has_key('glue'):
        try:
            work = models.safe_get_work(identifiers['glue'])
            return work.preferred_edition
        except:
            pass
    
    if identifiers.has_key('http'):
        edition = add_by_webpage(identifiers['http'], user=user)
        return user_edition(edition, user)

    
    # return a dummy edition and identifier
    
    title = '!!! missing title !!!'
    work = models.Work.objects.create(title=title)
    edition = models.Edition.objects.create(title='!!! missing title !!!', work=work)
    for key in identifiers.keys():
        if key == 'glue':
            id_value = work.id
        if key not in ('http', 'goog', 'oclc', 'isbn'):
            if key in WORK_IDENTIFIERS:
                edid = str(edition.id)
                models.Identifier.objects.create(type='edid', value=edid, work=work, edition=edition)  
                models.Identifier.objects.create(type=key, value=id_value, work=work, edition=None) 
            else:
                models.Identifier.objects.create(type=key, value=id_value, work=work, edition=edition)
    return user_edition(edition, user)

@login_required
def new_edition(request, by=None):
    '''
    view for creating editions
    '''
    alert = ''
    if request.method == 'POST':
        form = IdentifierForm(data=request.POST)
        if form.is_valid():
            if form.cleaned_data.get('make_new', False):
                edition = get_edition_for_id('glue', 'new', user=request.user)
            else:
                id_type = form.cleaned_data['id_type']
                id_value = form.cleaned_data['id_value']
                identifiers = models.Identifier.objects.filter(type=id_type, value=id_value)
                if identifiers:
                    # pre-existing identifier
                    ident = identifiers[0]
                    work = ident.work
                    edition = ident.edition if ident.edition else work.preferred_edition
                else:
                    edition = get_edition_for_id(id_type, id_value, user=request.user)
            
            return HttpResponseRedirect(
                reverse('new_edition', kwargs={
                    'work_id': edition.work_id,
                    'edition_id': edition.id
                })
            )
    else:
        form = IdentifierForm()
    return render(request, 'new_edition.html', {'form': form, 'alert':alert})

@login_required
def edit_edition(request, work_id, edition_id, by=None):
    '''
    view for editing  editions
    '''
    if not work_id and not edition_id:
        return new_edition(request, by=by)
    # if the work and edition are set, we save the edition and set the work
    language = 'en'
    age_level = ''
    description = ''
    title = ''
    if work_id:
        work = safe_get_work(work_id)
        language = work.language
        age_level = work.age_level
        description = work.description
        title = work.title
    else:
        work = None

    alert = ''
    admin = user_can_edit_work(request.user, work)
    if edition_id:
        edition = get_edition(edition_id)
        if work:
            edition.work = work
        language = edition.work.language
        age_level = edition.work.age_level
        description = edition.work.description
    else:
        edition = models.Edition()
        if work:
            edition.work = work
            edition.publication_date = work.earliest_publication_date
            edition.new_authors = []
            for relator in work.relators():
                edition.new_authors.append((relator.author.name, relator.relation.code))

    initial = {
        'language': language,
        'age_level': age_level,
        'publisher_name': edition.publisher_name,
        'description': description,
        'title': title,
    } 
    if request.method == 'POST':
        keep_editing = request.POST.has_key('add_author_submit')
        form = None
        edition.new_authors = zip(
            request.POST.getlist('new_author'),
            request.POST.getlist('new_author_relation')
        )
        edition.new_subjects = request.POST.getlist('new_subject')
        if edition.id and admin:
            for author in edition.authors.all():
                if request.POST.has_key('delete_author_%s' % author.id):
                    edition.remove_author(author)
                    form = EditionForm(instance=edition, data=request.POST, files=request.FILES)
                    keep_editing = True
                    break
            work_rels = models.WorkRelation.objects.filter(Q(to_work=work) | Q(from_work=work))
            for work_rel in work_rels:
                if request.POST.has_key('delete_work_rel_%s' % work_rel.id):
                    work_rel.delete()
                    form = EditionForm(instance=edition, data=request.POST, files=request.FILES)
                    keep_editing = True
                    break
            activate_all = request.POST.has_key('activate_all_ebooks')
            deactivate_all = request.POST.has_key('deactivate_all_ebooks')
            ebookchange = False
            if request.POST.has_key('set_ebook_rights') and request.POST.has_key('set_rights'):
                rights = request.POST['set_rights']
                for ebook in work.ebooks_all():
                    ebook.rights = rights
                    ebook.save()
                    ebookchange = True
            for ebook in work.ebooks_all():
                if request.POST.has_key('activate_ebook_%s' % ebook.id) or activate_all:
                    ebook.activate()
                    ebookchange = True
                elif request.POST.has_key('deactivate_ebook_%s' % ebook.id) or deactivate_all:
                    ebook.deactivate()
                    ebookchange = True
            if ebookchange:
                keep_editing = True
                form = EditionForm(instance=edition, data=request.POST, files=request.FILES)
        
        if request.POST.get('add_author', None) and admin:
            new_author_name = request.POST['add_author'].strip()
            new_author_relation =  request.POST['add_author_relation']
            if (new_author_name, new_author_relation) not in edition.new_authors:
                edition.new_authors.append((new_author_name, new_author_relation))
        form = EditionForm(instance=edition, data=request.POST, files=request.FILES)
        if not keep_editing and admin:
            if form.is_valid():
                form.save()
                if not work:
                    work = models.Work(
                        title=form.cleaned_data['title'],
                        language=form.cleaned_data['language'],
                        age_level=form.cleaned_data['age_level'],
                        description=form.cleaned_data['description'],
                    )
                    work.save()
                    edition.work = work
                    edition.save()
                else:
                    work.description = form.cleaned_data['description']
                    work.title = form.cleaned_data['title']
                    work.publication_range = None  # will reset on next access
                    work.language = form.cleaned_data['language']
                    work.age_level = form.cleaned_data['age_level']
                    work.save(update_fields=[
                        'title',
                        'description',
                        'publication_range',
                        'language',
                        'age_level'
                    ])

                id_type = form.cleaned_data['id_type']
                id_val = form.cleaned_data['id_value']
                if id_val == 'delete':
                    if id_type in WORK_IDENTIFIERS:
                        if edition.work.identifiers.exclude(type=id_type):
                            edition.work.identifiers.filter(type=id_type).delete()
                        else:
                            alert = ('Can\'t delete identifier -  must have at least one left.')
                    else:
                        if edition.identifiers.exclude(type=id_type):
                            edition.identifiers.filter(type=id_type).delete()
                        else:
                            alert = ('Can\'t delete identifier -  must have at least one left.')
                elif id_val:
                    models.Identifier.set(
                        type=id_type,
                        value=id_val,
                        edition=edition,
                        work=work
                    )
                for relator in edition.relators.all():
                    if request.POST.has_key('change_relator_%s' % relator.id):
                        new_relation = request.POST['change_relator_%s' % relator.id]
                        relator.set(new_relation)
                related_work = form.cleaned_data['add_related_work']
                if related_work:
                    models.WorkRelation.objects.get_or_create(
                        to_work=work,
                        from_work=related_work,
                        relation=form.cleaned_data['add_work_relation'],
                    )
                for (author_name, author_relation) in edition.new_authors:
                    edition.add_author(author_name, author_relation)
                if form.cleaned_data.has_key('bisac'):
                    bisacsh = form.cleaned_data['bisac']
                    while bisacsh:
                        add_subject(bisacsh.full_label, work, authority="bisacsh")
                        bisacsh = bisacsh.parent
                for subject_name in edition.new_subjects:
                    add_subject(subject_name, work)
                work_url = reverse('work', kwargs={'work_id': edition.work_id})
                cover_file = form.cleaned_data.get("coverfile", None)
                if cover_file:
                    # save it
                    cover_file_name = '/Users/%s/covers/%s/%s' % (
                        request.user.username,
                        edition.pk,
                        cover_file.name
                    )
                    new_file = default_storage.open(cover_file_name, 'w')
                    new_file.write(cover_file.read())
                    new_file.close()
                    #and put its url into cover_image
                    edition.cover_image = default_storage.url(cover_file_name)
                    edition.save()
                if not alert:
                    return HttpResponseRedirect(work_url)
    else:
        form = EditionForm(instance=edition, initial=initial)
        
    return render(request, 'edit_edition.html', {
            'form': form,
            'identform': IdentifierForm(),
            'edition': edition,
            'admin': admin,
            'alert': alert,
        })

