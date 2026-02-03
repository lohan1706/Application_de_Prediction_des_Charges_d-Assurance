from django import forms
from .models import Profile, CustomUser


SEX_CHOICES = [
    ("male", "Male"),
    ("female", "Female"),
]

REGION_CHOICES = [
    ("northwest", "Northwest"),
    ("northeast", "Northeast"),
    ("southwest", "Southwest"),
    ("southeast", "Southeast"),
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
        fields = ['age', 'sex', 'bmi', 'children', 'smoker', 'region']

        labels = {
            'age': 'Âge',
            'sex': 'Sexe',
            'bmi': 'IMC',
            'children': "Nombre d'enfants",
            'smoker': 'Fumeur',
            'region': 'Région',
        }

        widgets = {
            'age': forms.NumberInput(attrs={'class': 'form-control'}),

            'sex': forms.Select(
                choices=SEX_CHOICES,
                attrs={'class': 'form-control'}
            ),

            'bmi': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),

            'children': forms.NumberInput(attrs={'class': 'form-control'}),

            'smoker': forms.Select(
                choices=SMOKER_CHOICES,
                attrs={'class': 'form-control'}
            ),

            'region': forms.Select(
                choices=REGION_CHOICES,
                attrs={'class': 'form-control'}
            ),
        }