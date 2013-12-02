import logging
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.views import login
from django.contrib.auth import login as login_to_user
from django.contrib.auth import load_backend
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView, CreateView, UpdateView, SingleObjectMixin
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
        self.backend_class=getattr(backends,self.library.backend)
        form_class = self.backend_class.form
        if form_class:
            self.form = form_class(request, library, *args, **kwargs)
        else:
            self.form = None
        
    def process(self, success_url, deny_url):
        logger.info('authenticator for %s at %s.'%(self.request.user, self.library))
        if self.library.has_user(self.request.user):
            return HttpResponseRedirect(success_url)
        
        if self.backend_class().authenticate(self.request, self.library):
            if self.request.user.is_authenticated():
                self.library.add_user(self.request.user)
                return HttpResponseRedirect(success_url)
            else:
                return superlogin(self.request, extra_context={'library':self.library}, template_name='libraryauth/library_login.html')
            
        else:
            return self.backend_class.authenticator().process(success_url, deny_url)
            
    def allowed(self):
        return  self.backend_class.authenticate(self.request, self.library)

class BaseLibraryView:
    model = Library 
    template_name="libraryauth/edit.html"
    

class CreateLibraryView(BaseLibraryView, CreateView):
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

class UpdateLibraryView(BaseLibraryView, UpdateView):
    pk_url_kwarg =  'library_id'
    form_class = LibraryForm
    
    def form_valid(self, form):
        context_data = self.get_context_data(form=form)
        form.instance.save()
        context_data['status'] = 'Library Updated.'
        return self.render_to_response(context_data)

    def get_backend_form_class(self):
        if self.object and self.object.backend:
            backend_class=getattr(backends,self.object.backend)
            return backend_class.admin_form
        else:
            return None
            
    def get_backend_admin_forms(self):
        if self.object and self.object.backend:
            backend_models_name = '%s_auths' % self.object.backend
            backend_models = getattr(self.object,backend_models_name)
            backend_new_form = self.get_backend_form_class()(initial = {'library':self.object}, prefix="new")
            backend_old_forms = [self.get_backend_form_class()(instance = backend_model, prefix="backend_%s"%backend_model.id) for backend_model in backend_models.all()]
            return backend_old_forms + [backend_new_form]
        else:
            return []
            
    def get_context_data(self, backend_form=None, form=None, **kwargs):
        context = super(UpdateLibraryView,self).get_context_data(**kwargs)
        backend_admin_forms = self.get_backend_admin_forms()
        if backend_form:
            backend_admin_forms = [ backend_form if backend_form.prefix== backend_admin_form.prefix else backend_admin_form for backend_admin_form in backend_admin_forms] 
        context['backend_admin_forms'] = backend_admin_forms
        if form:
            context['form'] = form
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        # check permissions
        if request.user not in [self.object.owner, self.object.user]:
            context_data={'status': 'You\'re not permitted to edit this library.'}
            return self.render_to_response(context_data)
        form = self.get_form(self.form_class)
        return self.render_to_response(self.get_context_data(form=form))
        
    def post(self, request, *args, **kwargs):
        # get the user instance (the library)
        self.object = self.get_object()
        # check permissions
        if request.user not in [self.object.owner, self.object.user]:
            context_data={'status': 'You\'re not permitted to edit this library.'}
            return self.render_to_response(context_data)
        # determine if backend form is being submitted
        # uses the name of the form's submit button
        if 'backend_submit' in request.POST or 'backend_delete' in request.POST:
            # get the form
            form_class = self.get_backend_form_class()
            form_model = form_class.Meta.model
            backend_id = request.POST['id']
            if 'backend_submit' in request.POST:
                # we're editing the backend
                if backend_id is None or backend_id=="None":
                    backend_model_instance = form_model(library=self.object)
                    form = form_class(data=request.POST, instance=backend_model_instance, prefix="new")
                else:
                    backend_model_instance = form_model.objects.get(id=backend_id)
                    form = form_class(data=request.POST, instance=backend_model_instance, prefix="backend_%s"%request.POST['id'])
                if form.is_valid():
                    form.save()
                    status = 'User Validation Updated.'
                    context_data = self.get_context_data( form=self.form_class(instance=self.object))
                else:
                    status = 'Problem with User Validation.'
                    context_data = self.get_context_data(backend_form=form, form=self.form_class(instance=self.object))
            else:
                #deleting a backend
                if backend_id is not None and backend_id!="None":
                    backend_model_instance = form_model.objects.get(id=backend_id)
                    backend_model_instance.delete()
                    status = 'Deleted.'
                context_data = self.get_context_data( form=self.form_class(instance=self.object))
            context_data['status'] = status
            return self.render_to_response(context_data)
        else:
            # just use regular post handler 
            form = self.get_form(self.form_class)
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
                
@login_required
def login_as_library(request, library_id):   
    library=get_library_or_404(library_id=library_id)
    if request.user == library.owner:
        login_user(request, library.user)
            
    return HttpResponseRedirect(reverse('library_admin',args=[library.id]))


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