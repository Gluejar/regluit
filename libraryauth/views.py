import logging
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.views import login
from django.contrib.auth import login as login_to_user
from django.contrib.auth import load_backend
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView, CreateView, UpdateView
from . import backends

from .models import Library
from .forms import AuthForm, LibraryForm, NewLibraryForm

logger = logging.getLogger(__name__)

def get_library_or_404(library=None,  library_id=None):
    if library_id:
        return get_object_or_404(Library, id=library_id)
    else:
        return get_object_or_404(Library, user__username=library)

def library(request, library=None,  library_id=None,
        extra_context={}, 
        template='libraryauth/library.html',
        **kwargs):
    library=get_library_or_404(library=library, library_id=library_id)
    context={   'library':library, 
                'is_admin':  request.user.is_staff or request.user==library.user,
                'is_member': request.user.is_staff or library.has_user(request.user),
            }
    context.update(extra_context)
    return render(request, template, context)

def join_library(request, library_id):
    library=get_library_or_404(library_id=library_id)
    return Authenticator(request,library).process(
            reverse('library',args=[library.user]), 
            reverse('bad_library',args=[library.id]), 
        )

def superlogin(request, extra_context=None, **kwargs):
    if request.method == 'POST' and request.user.is_anonymous():
        username=request.POST.get("username", "")
        try:
            user=models.User.objects.get(username=username)
            extra_context={"socials":user.profile.social_auths}
        except:
            pass
    if request.GET.has_key("add"):
        request.session["add_wishlist"]=request.GET["add"]
    return login(request, extra_context=extra_context, authentication_form=AuthForm, **kwargs)

class Authenticator:
    request=None
    library=None

    def __init__(self, request, library, *args, **kwargs):
        self.request = request
        if  isinstance(library , basestring):
            self.library = Library.objects.get(user__username=library)
        elif isinstance(library , Library):
            self.library=library
        else:
            raise Exception
        try:
            form_class = getattr(backends, self.library.backend + '_form')
            self.form = form_class(request, library, *args, **kwargs)
        except AttributeError:
            self.form = None
        
    def process(self, success_url, deny_url):
        logger.info('authenticator for %s at %s.'%(self.request.user, self.library))
        if self.library.has_user(self.request.user):
            return HttpResponseRedirect(success_url)
        backend_test= getattr(backends, self.library.backend + '_authenticate')
        if backend_test(self.request, self.library):
            if self.request.user.is_authenticated():
                self.library.add_user(self.request.user)
                return HttpResponseRedirect(success_url)
            else:
                return superlogin(self.request, extra_context={'library':self.library}, template_name='libraryauth/library_login.html')
            
        else:
            backend_authenticator= getattr(backends, self.library.backend + '_authenticator')
            return backend_authenticator().process(self, success_url, deny_url)
            
    def allowed(self):
        backend_test= getattr(backends, self.library.backend + '_authenticate')
        return  backend_test(self.request, self.library)

class CreateLibraryView(CreateView):
    model = Library 
    template_name="libraryauth/edit.html"
    form_class = NewLibraryForm
    
    def get_initial(self):
        return {'email': self.request.user.email}

    def form_valid(self, form):
        form.instance.owner =  self.request.user
        user = form.instance.user
        user.email = form.cleaned_data['email']
        user.save()
        form.instance.user = user
        form.instance.save()
        context_data = self.get_context_data(form=form)
        context_data['status'] = 'Library Updated'
        return HttpResponseRedirect(reverse('library_admin',args=[form.instance.id]))

    
class UpdateLibraryView(UpdateView):
    model = Library 
    pk_url_kwarg =  'library_id'
    template_name="libraryauth/edit.html"
    form_class = LibraryForm
    
    def form_valid(self, form):
        if self.request.user in [form.instance.owner, form.instance.user]:
            form.instance.save()
            context_data = self.get_context_data(form=form)
            context_data['status'] = 'Library Updated.'
        else:
            context_data['status'] = 'You\'re not permitted to edit this library.'
        return self.render_to_response(context_data)
    
@login_required
def login_as_library(request, library_id):   
    library=get_library_or_404(library_id=library_id)
    if request.user == library.owner:
        login_user(request, library.user)
            
        return HttpResponseRedirect(reverse('library',args=[library.user]))
    else:
        return HttpResponseRedirect(reverse('library_admin',args=[library.user]))


def login_user(request, user):
    """
    Log in a user without requiring credentials (using ``login`` from
    ``django.contrib.auth``, first finding a matching backend).
    magic from https://djangosnippets.org/snippets/1547/

    """
    if not hasattr(user, 'backend'):
        for backend in settings.AUTHENTICATION_BACKENDS:
            if user == load_backend(backend).get_user(user.pk):
                user.backend = backend
                break
    if hasattr(user, 'backend'):
        return login_to_user(request, user)