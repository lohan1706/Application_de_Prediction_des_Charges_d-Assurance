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
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '')
        return first_name.strip()
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', '')
        return last_name.strip()
    
    def clean_email(self):
        """Validation du type et unitcité du mail"""
        email = self.cleaned_data.get('email')
        if email:
            # verifier si email appartient à un autre utilisateur
            qs = CustomUser.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Cet e-mail est déjà utilisé.")
        return email

class ProfileForm(forms.ModelForm):
    smoker = forms.BooleanField(required=False, label='Fumeur')
    
    class Meta:
        model = Profile
        fields = ['age', 'sex', 'height', 'weight', 'children', 'smoker', 'region']

        labels = {
            'age': 'Âge',
            'sex': 'Sexe',
            'height': 'Taille (m)',
            'weight': 'Poids (kg)',
            'children': "Nombre d'enfants",
            'region': 'Région',
        }

        widgets = {
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'sex': forms.Select(choices=SEX_CHOICES, attrs={'class': 'form-control'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'region': forms.Select(choices=REGION_CHOICES, attrs={'class': 'form-control'}),
        }
    
    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is None:
            raise forms.ValidationError("L'âge est requis.")
        if age < 18:
            raise forms.ValidationError("L'âge doit être au moins 18 ans.")
        if age < 0:
            raise forms.ValidationError("L'âge doit être un entier nul ou positif.")
        return age
    
    def clean_bmi(self):
        bmi = self.cleaned_data.get('bmi')
        if bmi is not None and (bmi <= 0 or bmi > 100):
            raise forms.ValidationError("Le BMI doit être un nombre positif raisonnable.")
        return bmi
    
    def clean_children(self):
        children = self.cleaned_data.get('children')
        if children is None or children < 0:
            raise forms.ValidationError("Le nombre d'enfants doit être un entier nul ou positif.")
        return children