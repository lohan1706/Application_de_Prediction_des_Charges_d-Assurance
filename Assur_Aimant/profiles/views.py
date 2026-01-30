from django.views.generic import UpdateView
from django.urls import reverse_lazy
from .models import Profile
from .forms import ProfileForm

from assur_predict.views import model, rmse
from assur_predict.models import Prediction

import pandas as pd


class ProfileView(UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "profiles/profile.html"
    success_url = reverse_lazy("profile")

    def get_object(self):
        return self.request.user.profile

    def form_valid(self, form):
        profile = form.save()

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
            user=profile.user,
            predicted_charge=float(result)
        )

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        last_pred = Prediction.objects.filter(
            user=self.request.user
        ).last()
        context["prediction"] = last_pred
        context["rmse"] = rmse

        return context
