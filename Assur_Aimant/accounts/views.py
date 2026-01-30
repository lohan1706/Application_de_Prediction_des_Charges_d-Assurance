from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm

class SignupView(CreateView):
    """
    Vue d'inscription utilisateur
    """   
    form_class = CustomUserCreationForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        messages.success(self.request, "Compte créé avec succès. Vous pouvez vous connecter.")
        return super().form_valid(form)


class CustomLoginView(LoginView):
    """
    Vue de connexion utilisateur
    """
    template_name = "accounts/login.html"

    def form_valid(self, form):
        messages.success(self.request, "Connexion réussie.")
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    """
    Vue de déconnexion utilisateur
    """
    next_page = reverse_lazy("login")
