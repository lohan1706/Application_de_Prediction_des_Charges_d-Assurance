from django import forms
from .models import Profile

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
            'sex': forms.TextInput(attrs={'class': 'form-control'}),
            'bmi': forms.NumberInput(attrs={'class': 'form-control'}),
            'children': forms.NumberInput(attrs={'class': 'form-control'}),
            'smoker': forms.CheckboxInput(),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
        }