from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from profiles.models import Profile
from .models import Prediction
from .services import model, rmse
import pandas as pd


class PredictView(LoginRequiredMixin, TemplateView):
    template_name = "prediction/predict.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            profile = Profile.objects.get(user=self.request.user)
            context["profile"] = profile
            
            last_prediction = Prediction.objects.filter(
                user=self.request.user
            ).first()
            context["prediction"] = last_prediction
            
            history = Prediction.objects.filter(
                user=self.request.user
            )[:5]
            context["history"] = history
            
            context["rmse"] = rmse

            if last_prediction:
                show_rmse = (last_prediction.predicted_charge - rmse) >= 1000
                context["show_rmse"] = show_rmse
            
        except Profile.DoesNotExist:
            context["profile"] = None
            messages.warning(
                self.request, 
                "Veuillez compléter votre profil avant de faire une prédiction."
            )

        return context

    def post(self, request, *args, **kwargs):
        try:
            profile = Profile.objects.get(user=request.user)

            data = {
                "age": profile.age,
                "sex": profile.sex,
                "bmi": profile.bmi,
                "children": profile.children,
                "smoker": "yes" if profile.smoker else "no",
                "region": profile.region,
            }

            df = pd.DataFrame([data])
            result = model.predict(df)[0]

            Prediction.objects.create(
                user=request.user,
                predicted_charge=float(result)
            )

            messages.success(request, "Prédiction effectuée avec succès!")

        except Profile.DoesNotExist:
            messages.error(
                request, 
                "Erreur: Profil introuvable. Veuillez créer votre profil d'abord."
            )
        except Exception as e:
            messages.error(request, f"Erreur lors de la prédiction: {str(e)}")

        return self.get(request, *args, **kwargs)