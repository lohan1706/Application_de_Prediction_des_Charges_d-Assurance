from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from .models import Profile
from django.contrib.auth.mixins import LoginRequiredMixin

# from django.contrib.auth import get_user_model

# User = get_user_model()

from .forms import ProfileForm

class ProfileView(UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'profiles/profile.html'
    success_url = reverse_lazy("profile")

    def get_object(self):
        return Profile.objects.first()
