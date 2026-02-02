from django.views.generic import UpdateView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Profile
from .forms import ProfileForm, PredictionForm  # Importez les deux formulaires
from assur_predict.views import model, rmse
from assur_predict.models import Prediction
import pandas as pd


class ProfileView(UpdateView):
    """Vue pour gérer uniquement le profil utilisateur"""
    model = Profile
    form_class = ProfileForm
    template_name = "profiles/profile.html"
    success_url = reverse_lazy("profile")
    
    def get_object(self):
        profile, created = Profile.objects.get_or_create(
            user=self.request.user,
            defaults={
                "age": 18,
                "sex": "male",
                "bmi": 20,
                "children": 0,
                "smoker": False,
                "region": "northwest",
            }
        )
        return profile
    
    def form_valid(self, form):
        messages.success(self.request, 'Profil mis à jour avec succès!')
        return super().form_valid(form)


class PredictionView(FormView):
    """Vue pour faire une prédiction"""
    form_class = PredictionForm
    template_name = "profiles/prediction.html"
    success_url = reverse_lazy("prediction")
    
    def get_initial(self):
        """Pré-remplir le formulaire avec les données du profil"""
        profile, created = Profile.objects.get_or_create(
            user=self.request.user,
            defaults={
                "age": 18,
                "sex": "male",
                "bmi": 20,
                "children": 0,
                "smoker": False,
                "region": "northwest",
            }
        )
        return {
            "age": profile.age,
            "sex": profile.sex,
            "bmi": profile.bmi,
            "children": profile.children,
            "smoker": profile.smoker,
            "region": profile.region,
        }
    
    def form_valid(self, form):
        # Récupérer les données du formulaire
        data = {
            "age": form.cleaned_data["age"],
            "sex": form.cleaned_data["sex"],
            "bmi": form.cleaned_data["bmi"],
            "children": form.cleaned_data["children"],
            "smoker": "yes" if form.cleaned_data["smoker"] else "no",
            "region": form.cleaned_data["region"],
        }
        
        # Faire la prédiction
        df = pd.DataFrame([data])
        result = model.predict(df)[0]
        
        # Sauvegarder la prédiction
        Prediction.objects.create(
            user=self.request.user,
            predicted_charge=float(result)
        )
        
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Récupérer la dernière prédiction
        last_pred = Prediction.objects.filter(
            user=self.request.user
        ).last()
        
        context["prediction"] = last_pred
        context["rmse"] = rmse
        return context