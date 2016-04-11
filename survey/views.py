import logging

from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView

from .models import Landing


        
class SurveyView(TemplateView):
    template_name = "survey/generic.html"

    def get_context_data(self, **kwargs):
        context = super(SurveyView, self).get_context_data(**kwargs)
        
        nonce = self.kwargs['nonce']
        landing = get_object_or_404(Landing, nonce=nonce)
        context["landing"] = landing

        return context    
