from django.shortcuts import render
import joblib
from django.conf import settings
from pathlib import Path

# Chemin absolu vers le modèle ML
MODEL_PATH = Path(settings.BASE_DIR) / "assur_predict" / "ml" / "gb_pipeline.joblib"
RMSE_PATH = Path(settings.BASE_DIR) / "assur_predict" / "ml" / "rmse.joblib"

# Charger les modèles
model = joblib.load(MODEL_PATH)
rmse = joblib.load(RMSE_PATH)

def home(request):
    return render(request, 'assur_predict/home.html')


class HomeView(TemplateView):
    template_name = "assur_predict/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titre"] = "Bienvenue sur AssurPredict"
        return context
