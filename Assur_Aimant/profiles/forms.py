from django import forms
from .models import Profile

# Gardez votre ProfileForm existant
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['age', 'sex', 'bmi', 'children', 'smoker', 'region']
        # ... votre configuration existante

# NOUVEAU : Ajoutez ce formulaire
class PredictionForm(forms.Form):
    """Formulaire pour faire une prédiction sans modifier le profil"""
    age = forms.IntegerField(
        label='Âge',
        min_value=18,
        max_value=100,
    )
    sex = forms.ChoiceField(
        label='Sexe',
        choices=[('male', 'Homme'), ('female', 'Femme')],
    )
    bmi = forms.FloatField(
        label='IMC (Indice de Masse Corporelle)',
        min_value=10,
        max_value=60,
    )
    children = forms.IntegerField(
        label='Nombre d\'enfants',
        min_value=0,
        max_value=10,
    )
    smoker = forms.BooleanField(
        label='Fumeur',
        required=False,
    )
    region = forms.ChoiceField(
        label='Région',
        choices=[
            ('northwest', 'Nord-Ouest'),
            ('northeast', 'Nord-Est'),
            ('southwest', 'Sud-Ouest'),
            ('southeast', 'Sud-Est'),
        ],
    )