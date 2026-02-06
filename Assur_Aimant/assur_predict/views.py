from django.shortcuts import render
from django.conf import settings
from django.views.generic import TemplateView
from pathlib import Path
import joblib

class HomeView(TemplateView):
    template_name = "assur_predict/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titre"] = "Bienvenue sur AssurPredict"
        return context

MODEL_PATH = Path(settings.BASE_DIR) / "assur_predict" / "ml" / "gb_pipeline.joblib"

_model = None

def get_model():
    global _model
    if _model is None:
        try:
            _model = joblib.load(MODEL_PATH)
        except Exception as e:
            _model = None
            # en dev affiche l'erreur ; en prod utilisez logging
            print("assur_predict: failed to load model:", e)
    return _model