# Create your views here.
from django.shortcuts import render_to_response
from django.conf import settings
from django.template import RequestContext
from django import http
from django.utils import translation
from .models import Page

def page(request, page_to_render):
    try:
        p = Page.objects.get(slug=page_to_render, public=True)
    except Page.DoesNotExist:
        return render_to_response("pages/{}.html".format(page_to_render), 
            { "request" : request,}, 
            context_instance = RequestContext(request) 
        )
    
    return render_to_response("page.html", 
            { "request" : request, "page" : p, }, 
            context_instance = RequestContext(request) 
        )

def langpage(request, lang, page_to_trans):
    translation.activate(lang)
    return page(request, page_to_trans)

def set_language(request):
    next = request.POST.get('next', request.GET.get('next', None))
    if not next:
        next = request.META.get('HTTP_REFERER', None)
        if not next:
            next = '/'
    response = http.HttpResponseRedirect(next)
    if request.method == 'GET':
        lang_code = request.GET.get('language', None)
        if lang_code and translation.check_for_language(lang_code):
            if hasattr(request, 'session'):
                request.session['django_language'] = lang_code
            else:
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
    return response

