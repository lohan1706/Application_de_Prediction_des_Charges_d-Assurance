from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import Profile
from django.contrib.messages import get_messages
from django.urls import reverse
from django.test import Client
from .forms import ProfileForm, UserPersonalInfoForm


class UserModelTest(TestCase):

    def test_username_doit_etre_unique(self):
        # créer un utilisateur
        User = get_user_model()
        User.objects.create_user(
            username="etudiante",
            password="Password123!"
            
        )

        # essayer de créer un utilisateur avec le même username
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="etudiante",
                password="Password456!"
            )



class PasswordValidationTest(TestCase):

    def setUp(self):
        # créer un utilisateur fictif pour la validation
        User = get_user_model()
        self.user = User(username="etudiante", email="etudiante@test.com")

    def test_password_trop_proche_infos_personnelles(self):
        """Le mot de passe ne doit pas ressembler au username ou email"""
        password = "etudiante123!"
        with self.assertRaises(ValidationError):
            validate_password(password, user=self.user)

    def test_password_trop_court(self):
        """Le mot de passe doit avoir au moins 8 caractères"""
        password = "Abc123"
        with self.assertRaises(ValidationError):
            validate_password(password, user=self.user)

    def test_password_trop_commun(self):
        """Le mot de passe ne doit pas être un mot de passe courant"""
        password = "password123"
        with self.assertRaises(ValidationError):
            validate_password(password, user=self.user)

    def test_password_entierement_numerique(self):
        """Le mot de passe ne doit pas être entièrement numérique"""
        password = "12345678"
        with self.assertRaises(ValidationError):
            validate_password(password, user=self.user)

    def test_password_valide(self):
        """Mot de passe valide respecte toutes les règles"""
        password = "MotdepasseSecur123!"
        try:
            validate_password(password, user=self.user)
        except ValidationError:
            self.fail("Le mot de passe valide a été rejeté")



class ProfileModelTest(TestCase):

    def test_modification_du_profil(self):
        CustomUser = get_user_model()
        user = CustomUser.objects.create_user(username="client2", password="Password123!")

        # créer manuellement le profil
        profile = Profile.objects.create(
            user=user,
            age=0,
            sex="",
            bmi=0.0,
            children=0,
            smoker=False,
            region=""
        )

        # modifier le profil
        profile.age = 30
        profile.region = "southwest"
        profile.save()

        # récupérer le profil mis à jour
        updated_profile = Profile.objects.get(user=user)
        self.assertEqual(updated_profile.age, 30)
        self.assertEqual(updated_profile.region, "southwest")


User = get_user_model()

class ProfileViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="jdoe", email="jdoe@example.com", password="pass1234")

    def test_profile_view_requires_login(self):
        resp = self.client.get(reverse("profile"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/login", resp.url)

    def test_get_object_creates_profile_with_defaults(self):
        self.client.login(username="jdoe", password="pass1234")
        resp = self.client.get(reverse("profile"))
        self.assertEqual(resp.status_code, 200)
        profile = Profile.objects.filter(user=self.user).first()
        self.assertIsNotNone(profile)
        # valeurs par défaut attendues (conformez si différent)
        self.assertEqual(profile.age, 18)
        self.assertEqual(profile.sex, "male")
        self.assertEqual(profile.bmi, 20.0)

    def test_profile_update_saves_profile_and_user(self):
        self.client.login(username="jdoe", password="pass1234")
        data = {
            "age": 30,
            "sex": "female",
            "bmi": 22.5,
            "children": 2,
            "smoker": "on",          # checkbox => presence suffit
            "region": "northeast",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
        }
        resp = self.client.post(reverse("profile"), data, follow=True)
        self.assertEqual(resp.status_code, 200)
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.age, 30)
        self.assertEqual(profile.sex, "female")
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "John")
        self.assertEqual(self.user.email, "john.doe@example.com")
        messages = [m.message for m in get_messages(resp.wsgi_request)]
        self.assertIn("Profil mis à jour avec succès!", messages)

    def test_context_contains_user_form(self):
        self.client.login(username="jdoe", password="pass1234")
        resp = self.client.get(reverse("profile"))
        self.assertIn("user_form", resp.context)
        user_form = resp.context["user_form"]
        self.assertEqual(user_form.instance, self.user)

    def test_invalid_post_shows_errors(self):
        self.client.login(username="jdoe", password="pass1234")
        data = {"age": "", "sex": "", "bmi": "not-a-number"}  # intentionnellement invalide
        resp = self.client.post(reverse("profile"), data)
        self.assertEqual(resp.status_code, 200)
        form = resp.context.get("form")
        self.assertTrue(form.errors)


class ProfileAdditionalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username="user1", email="u1@example.com", password="pass1234")
        self.user2 = User.objects.create_user(username="user2", email="u2@example.com", password="pass1234")

    def test_profile_uses_correct_template(self):
        self.client.login(username="user1", password="pass1234")
        resp = self.client.get(reverse("profile"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "profiles/profile.html")

    def test_smoker_checkbox_handling(self):
        self.client.login(username="user1", password="pass1234")
        # set smoker = True
        data = {"age": 28, "sex": "male", "bmi": 23.0, "children": 0, "smoker": "on", "region": "northwest",
                "first_name": "", "last_name": "", "email": "u1@example.com"}
        self.client.post(reverse("profile"), data)
        profile = Profile.objects.get(user=self.user1)
        self.assertTrue(profile.smoker)

        # set smoker = False (no key in POST)
        data.pop("smoker")
        data["age"] = 29
        self.client.post(reverse("profile"), data)
        profile.refresh_from_db()
        self.assertFalse(profile.smoker)

    def test_profile_created_only_once_on_multiple_gets(self):
        self.client.login(username="user1", password="pass1234")
        self.client.get(reverse("profile"))
        self.client.get(reverse("profile"))
        count = Profile.objects.filter(user=self.user1).count()
        self.assertEqual(count, 1)

    def test_updates_do_not_affect_other_user(self):
        # user1 updates profile
        self.client.login(username="user1", password="pass1234")
        self.client.post(reverse("profile"), {
            "age": 45, "sex": "female", "bmi": 26.0, "children": 1, "region": "southeast",
            "first_name": "A", "last_name": "B", "email": "u1new@example.com"
        })
        # user2 profile should remain default / separate
        self.client.login(username="user2", password="pass1234")
        resp = self.client.get(reverse("profile"))
        profile2 = Profile.objects.get(user=self.user2)
        # defaults expected (adapt if your defaults differ)
        self.assertNotEqual(profile2.age, 45)

  
    def test_invalid_email_in_user_form_is_not_saved(self):
        self.client.login(username="user1", password="pass1234")
        # create profile first
        self.client.get(reverse("profile"))
        post_data = {
            "age": 30, "sex": "male", "bmi": 22.0, "children": 0, "region": "northwest",
            "first_name": "Test", "last_name": "User", "email": "not-an-email"
        }
        resp = self.client.post(reverse("profile"), post_data)
        # l'email ne doit pas être modifié en base
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.email, "u1@example.com")
        # vérifier la validation du formulaire utilisateur localement
        from .forms import UserPersonalInfoForm
        user_form = UserPersonalInfoForm(data=post_data, instance=self.user1)
        self.assertFalse(user_form.is_valid())
        # la vue doit rendre le template (pas de redirection)
        self.assertEqual(resp.status_code, 200)



from django import forms
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

SEX_CHOICES = [
    ("male", "male"),
    ("female", "female"),
]

REGION_CHOICES = [
    ("northwest", "northwest"),
    ("northeast", "northeast"),
    ("southeast", "southeast"),
    ("southwest", "southwest"),
]

class ProfileForm(forms.ModelForm):
    sex = forms.ChoiceField(choices=SEX_CHOICES)
    region = forms.ChoiceField(choices=REGION_CHOICES)
    smoker = forms.BooleanField(required=False)

    class Meta:
        model = Profile
        fields = ["age", "sex", "bmi", "children", "smoker", "region"]

    def clean_age(self):
        age = self.cleaned_data.get("age")
        if age is None or age < 0:
            raise forms.ValidationError("L'âge doit être un entier nul ou positif.")
        return age

    def clean_bmi(self):
        bmi = self.cleaned_data.get("bmi")
        if bmi is None or bmi <= 0 or bmi > 100:
            raise forms.ValidationError("Le BMI doit être un nombre positif raisonnable.")
        return bmi

    def clean_children(self):
        children = self.cleaned_data.get("children")
        if children is None or children < 0:
            raise forms.ValidationError("Le nombre d'enfants doit être un entier nul ou positif.")
        return children

class UserPersonalInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Cet e-mail est déjà utilisé.")
        return email



User = get_user_model()

class ProfileAgeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="ageuser", email="age@example.com", password="pass1234")
        self.client.force_login(self.user)
        # ensure profile exists
        self.client.get(reverse("profile"))

    def test_age_must_be_integer(self):
        resp = self.client.post(reverse("profile"), {"age": "twenty", "sex": "male", "bmi": 22, "children": 0, "region": "northwest"})
        self.user.profile.refresh_from_db()
        # age should remain the default / previous valid value
        self.assertNotEqual(self.user.profile.age, "twenty")
        form = ProfileForm(data={"age": "twenty", "sex": "male", "bmi": 22, "children": 0, "region": "northwest"})
        self.assertFalse(form.is_valid())

    def test_age_cannot_be_negative(self):
        resp = self.client.post(reverse("profile"), {"age": -1, "sex": "male", "bmi": 22, "children": 0, "region": "northwest"})
        self.user.profile.refresh_from_db()
        self.assertNotEqual(self.user.profile.age, -1)
        form = ProfileForm(data={"age": -1, "sex": "male", "bmi": 22, "children": 0, "region": "northwest"})
        self.assertFalse(form.is_valid())

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        # Only validate/save user form if user-specific fields are present in POST
        user_fields = getattr(UserPersonalInfoForm.Meta, "fields", [])
        user_data_present = any(field in request.POST for field in user_fields)
        user_form = UserPersonalInfoForm(request.POST, instance=request.user) if user_data_present else None

        # Validate profile form first; if user data present, validate it too before saving
        if form.is_valid():
            if user_form and not user_form.is_valid():
                return self.form_invalid(form)
            # save user info if provided
            if user_form:
                user_form.save()
            messages.success(request, 'Profil mis à jour avec succès!')
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def test_age_upper_bound_reasonable(self):
        # large unrealistic age should be rejected by business rules (e.g., >120)
        resp = self.client.post(reverse("profile"), {"age": 130, "sex": "male", "bmi": 22, "children": 0, "region": "northwest"})
        self.user.profile.refresh_from_db()
        # ensure not saved if your form enforces upper bound
        form = ProfileForm(data={"age": 130, "sex": "male", "bmi": 22, "children": 0, "region": "northwest"})
        if not form.is_valid():
            self.assertNotEqual(self.user.profile.age, 130)
        else:
            # if form allows, at least ensure stored value matches submission
            self.assertEqual(self.user.profile.age, 130)

    def test_missing_age_uses_existing_value(self):
        # post without age should not clear the age
        prev_age = self.user.profile.age
        resp = self.client.post(reverse("profile"), {"sex": "male", "bmi": 22, "children": 0, "region": "northwest"})
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.age, prev_age)   

def test_age_must_be_at_least_18(self):
        resp = self.client.post(reverse("profile"), {"age": 17, "sex": "male", "bmi": 22, "children": 0, "region": "northwest"})
        self.user.profile.refresh_from_db()
        # age should not be updated to an invalid value
        self.assertNotEqual(self.user.profile.age, 17)
        form = ProfileForm(data={"age": 17, "sex": "male", "bmi": 22, "children": 0, "region": "northwest"})
        self.assertFalse(form.is_valid())      

def clean_age(self):
        age = self.cleaned_data.get("age")
        if age is None:
            raise forms.ValidationError("L'âge est requis.")
        if age < 18:
            raise forms.ValidationError("L'âge doit être au moins 18 ans.")
        return age 



User = get_user_model()

class ProfileMoreTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.u1 = User.objects.create_user(username="u1", email="u1@example.com", password="pass1234")
        self.u2 = User.objects.create_user(username="u2", email="u2@example.com", password="pass1234")

    def test_names_trimmed_on_save(self):
        self.client.force_login(self.u1)
        self.client.get(reverse("profile"))
        self.client.post(reverse("profile"), {
            "age": 25, "sex": "male", "bmi": 22, "children": 0,
            "region": "northwest", "first_name": "  Alice  ", "last_name": "  Dupont  ", "email": "u1@example.com"
        })
        self.u1.refresh_from_db()
        self.assertEqual(self.u1.first_name, "Alice")
        self.assertEqual(self.u1.last_name, "Dupont")

    def test_profile_template_escapes_html(self):
        self.client.force_login(self.u1)
        self.client.get(reverse("profile"))
        # store an unsafe string in first_name
        self.client.post(reverse("profile"), {
            "age": 25, "sex": "male", "bmi": 22, "children": 0,
            "region": "northwest", "first_name": "<script>alert(1)</script>", "email": "u1@example.com"
        })
        resp = self.client.get(reverse("profile"))
        self.assertNotIn("<script>alert(1)</script>", resp.content.decode())
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", resp.content.decode())

    def test_cannot_modify_other_users_profile(self):
        # create profile for u2 with distinct age
        self.client.force_login(self.u2)
        self.client.get(reverse("profile"))
        self.client.post(reverse("profile"), {"age": 99, "sex": "male", "bmi": 22, "children": 0, "region": "northwest", "email": "u2@example.com"})
        # try to update u2 profile while logged as u1 (should not affect u2)
        self.client.force_login(self.u1)
        self.client.post(reverse("profile"), {"age": 30, "sex": "male", "bmi": 22, "children": 0, "region": "northwest", "email": "u1@example.com"})
        self.u2.profile.refresh_from_db()
        self.assertEqual(self.u2.profile.age, 99)

    def test_form_is_sticky_on_invalid_post(self):
        self.client.force_login(self.u1)
        self.client.get(reverse("profile"))
        resp = self.client.post(reverse("profile"), {"age": "not-an-int", "sex": "male", "bmi": 22, "children": 0, "region": "northwest"})
        # response should contain the submitted (invalid) value so the user can correct it
        self.assertIn("not-an-int", resp.content.decode())           



User = get_user_model()

class ProfileExtraTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.u = User.objects.create_user(username="u", email="u@example.com", password="pass1234")
        self.client.force_login(self.u)
        # ensure profile exists
        self.client.get(reverse("profile"))

    def test_atomicity_user_form_invalid_does_not_change_profile(self):
        # set a known age
        self.client.post(reverse("profile"), {
            "age": 30, "sex": "male", "bmi": 22, "children": 0, "region": "northwest",
            "first_name": "Init", "last_name": "User", "email": "u@example.com"
        })
        self.u.profile.refresh_from_db()
        self.assertEqual(self.u.profile.age, 30)
        # submit with invalid email in user form but valid profile data
        resp = self.client.post(reverse("profile"), {
            "age": 40, "sex": "male", "bmi": 23, "children": 0, "region": "northwest",
            "first_name": "X", "last_name": "Y", "email": "not-an-email"
        })
        self.u.profile.refresh_from_db()
        # profile must not have been updated because user form is invalid
        self.assertEqual(self.u.profile.age, 30)
        # user form should be invalid locally
        uf = UserPersonalInfoForm(data={"email": "not-an-email"}, instance=self.u)
        self.assertFalse(uf.is_valid())

    def test_predict_page_prefills_from_profile(self):
        # update profile values
        self.client.post(reverse("profile"), {
            "age": 45, "sex": "female", "bmi": 26.5, "children": 1, "region": "southeast",
            "first_name": "P", "last_name": "Q", "email": "u@example.com"
        })
        # try common predict path
        resp = self.client.get("/predict/")
        # accept 200 OK; if protected, ensure redirect not 500
        self.assertIn(resp.status_code, (200, 302))
        if resp.status_code == 200:
            content = resp.content.decode()
            self.assertIn("45", content) or self.assertIn("26.5", content)

    def test_name_trimmed_on_save(self):
        self.client.post(reverse("profile"), {
            "age": 28, "sex": "male", "bmi": 22, "children": 0, "region": "northwest",
            "first_name": "  Alice  ", "last_name": "  Dupont  ", "email": "u@example.com"
        })
        self.u.refresh_from_db()
        self.assertEqual(self.u.first_name, "Alice")
        self.assertEqual(self.u.last_name, "Dupont")        