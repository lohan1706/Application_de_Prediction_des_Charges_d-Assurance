from django import forms
from .models import Profile, CustomUser


SEX_CHOICES = [
    ("male", "Masculin"),
    ("female", "Féminin"),
]

REGION_CHOICES = [
    ("northwest", "Nord-ouest"),
    ("northeast", "Nord-est"),
    ("southwest", "Sud-ouest"),
    ("southeast", "Sud-est"),
]

SMOKER_CHOICES = [
    (True, "Oui"),
    (False, "Non"),
]

class UserPersonalInfoForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email']
        
        labels = {
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'email': 'Email',
        }
        
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['age', 'sex', 'height', 'weight', 'children', 'smoker', 'region']

        labels = {
            'age': 'Âge',
            'sex': 'Sexe',
            'height': 'Taille (m)',
            'weight': 'Poids (kg)',
            # 'bmi': 'IMC',
            'children': "Nombre d'enfants",
            'smoker': 'Fumeur',
            'region': 'Région',
        }

        widgets = {
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'sex': forms.Select(choices=SEX_CHOICES, attrs={'class': 'form-control'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'bmi': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
            # 'children': forms.NumberInput(attrs={'class': 'form-control'}),
            'smoker': forms.Select(choices=SMOKER_CHOICES, attrs={'class': 'form-control'}),
            'region': forms.Select(choices=REGION_CHOICES, attrs={'class': 'form-control'}),
        }
