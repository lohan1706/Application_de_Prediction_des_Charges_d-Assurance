from django.shortcuts import render
from django.conf import settings
from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = "assur_predict/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titre"] = "Bienvenue sur AssurPredict"
        return context
