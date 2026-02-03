from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Profile
from .forms import ProfileForm, UserPersonalInfoForm


class ProfileView(LoginRequiredMixin, UpdateView):
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
                "bmi": 20.0,
                "children": 0,
                "smoker": False,
                "region": "northwest",
            }
        )
        return profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'user_form' not in context:
            context['user_form'] = UserPersonalInfoForm(instance=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        user_form = UserPersonalInfoForm(request.POST, instance=request.user)
        
        if form.is_valid() and user_form.is_valid():
            user_form.save()
            messages.success(request, 'Profil mis à jour avec succès!')
            return self.form_valid(form)
        else:
            return self.form_invalid(form)