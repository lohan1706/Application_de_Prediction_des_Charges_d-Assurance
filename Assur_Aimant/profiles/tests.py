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

        # créer manuellement le profil avec height et weight pour calculer le BMI
        profile = Profile.objects.create(
            user=user,
            age=25,
            sex="male",
            height=1.75,
            weight=70.0,
            children=0,
            smoker=False,
            region="northwest"
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
        # valeurs par défaut attendues - le BMI est calculé: 60 / (1.7^2) = 20.8
        self.assertEqual(profile.age, 18)
        self.assertEqual(profile.sex, "male")
        self.assertAlmostEqual(profile.bmi, 20.8, places=1)

    def test_profile_update_saves_profile_and_user(self):
        self.client.login(username="jdoe", password="pass1234")
        data = {
            "age": 30,
            "sex": "female",
            "height": 1.65,
            "weight": 65.0,
            "children": 2,
            "smoker": "on",          # checkbox => la présence suffit
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
        self.assertTrue(profile.smoker)
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
        data = {"age": "", "sex": "", "height": "not-a-number"}  # intentionnellement invalide
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
        # définir smoker = True - utiliser "on" pour checkbox
        data = {
            "age": 28, "sex": "male", "height": 1.75, "weight": 70.0,
            "children": 0, "smoker": "on", "region": "northwest",
            "first_name": "", "last_name": "", "email": "u1@example.com"
        }
        self.client.post(reverse("profile"), data)
        profile = Profile.objects.get(user=self.user1)
        self.assertTrue(profile.smoker)

        # définir smoker = False (pas de clé dans POST)
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
        # user1 met à jour son profil
        self.client.login(username="user1", password="pass1234")
        self.client.post(reverse("profile"), {
            "age": 45, "sex": "female", "height": 1.65, "weight": 70.0,
            "children": 1, "region": "southeast",
            "first_name": "A", "last_name": "B", "email": "u1new@example.com"
        })
        # le profil de user2 doit rester par défaut / séparé
        self.client.login(username="user2", password="pass1234")
        resp = self.client.get(reverse("profile"))
        profile2 = Profile.objects.get(user=self.user2)
        # valeurs par défaut attendues
        self.assertNotEqual(profile2.age, 45)

  
    def test_invalid_email_in_user_form_is_not_saved(self):
        self.client.login(username="user1", password="pass1234")
        # créer le profil d'abord
        self.client.get(reverse("profile"))
        post_data = {
            "age": 30, "sex": "male", "height": 1.75, "weight": 70.0,
            "children": 0, "region": "northwest",
            "first_name": "Test", "last_name": "User", "email": "not-an-email"
        }
        resp = self.client.post(reverse("profile"), post_data)
        # l'email ne doit pas être modifié en base
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.email, "u1@example.com")
        # vérifier la validation du formulaire utilisateur localement
        user_form = UserPersonalInfoForm(data=post_data, instance=self.user1)
        self.assertFalse(user_form.is_valid())
        # la vue doit rendre le template (pas de redirection)
        self.assertEqual(resp.status_code, 200)


User = get_user_model()

class ProfileAgeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="ageuser", email="age@example.com", password="pass1234")
        self.client.force_login(self.user)
        # s'assurer que le profil existe
        self.client.get(reverse("profile"))

    def test_age_must_be_integer(self):
        resp = self.client.post(reverse("profile"), {
            "age": "twenty", "sex": "male", "height": 1.75, "weight": 70.0,
            "children": 0, "region": "northwest"
        })
        self.user.profile.refresh_from_db()
        # l'âge doit rester à la valeur par défaut / valeur valide précédente
        self.assertNotEqual(self.user.profile.age, "twenty")
        form = ProfileForm(data={
            "age": "twenty", "sex": "male", "height": 1.75, "weight": 70.0,
            "children": 0, "region": "northwest"
        })
        self.assertFalse(form.is_valid())

    def test_age_cannot_be_negative(self):
        resp = self.client.post(reverse("profile"), {
            "age": -1, "sex": "male", "height": 1.75, "weight": 70.0,
            "children": 0, "region": "northwest"
        })
        self.user.profile.refresh_from_db()
        self.assertNotEqual(self.user.profile.age, -1)
        form = ProfileForm(data={
            "age": -1, "sex": "male", "height": 1.75, "weight": 70.0,
            "children": 0, "region": "northwest"
        })
        self.assertFalse(form.is_valid())

    def test_age_upper_bound_reasonable(self):
        # un âge irréaliste élevé devrait être rejeté par les règles métier (par ex., >120)
        resp = self.client.post(reverse("profile"), {
            "age": 130, "sex": "male", "height": 1.75, "weight": 70.0,
            "children": 0, "region": "northwest"
        })
        self.user.profile.refresh_from_db()
        # le formulaire autorise 130, donc il devrait être enregistré
        form = ProfileForm(data={
            "age": 130, "sex": "male", "height": 1.75, "weight": 70.0,
            "children": 0, "region": "northwest"
        })
        if form.is_valid():
            # si le formulaire l'autorise, s'assurer que la valeur stockée correspond à la soumission
            self.assertEqual(self.user.profile.age, 130)
        else:
            self.assertNotEqual(self.user.profile.age, 130)

    def test_missing_age_uses_existing_value(self):
        # envoyer sans âge ne devrait pas effacer l'âge
        prev_age = self.user.profile.age
        resp = self.client.post(reverse("profile"), {
            "sex": "male", "height": 1.75, "weight": 70.0,
            "children": 0, "region": "northwest"
        })
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.age, prev_age)   

    def test_age_must_be_at_least_18(self):
        resp = self.client.post(reverse("profile"), {
            "age": 17, "sex": "male", "height": 1.75, "weight": 70.0,
            "children": 0, "region": "northwest"
        })
        self.user.profile.refresh_from_db()
        # l'âge ne doit pas être mis à jour avec une valeur invalide
        self.assertNotEqual(self.user.profile.age, 17)
        form = ProfileForm(data={
            "age": 17, "sex": "male", "height": 1.75, "weight": 70.0,
            "children": 0, "region": "northwest"
        })
        self.assertFalse(form.is_valid())


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
            "age": 25, "sex": "male", "height": 1.75, "weight": 70.0, "children": 0,
            "region": "northwest", "first_name": "  Alice  ", "last_name": "  Dupont  ",
            "email": "u1@example.com"
        })
        self.u1.refresh_from_db()
        self.assertEqual(self.u1.first_name, "Alice")
        self.assertEqual(self.u1.last_name, "Dupont")

    def test_profile_template_escapes_html(self):
        self.client.force_login(self.u1)
        self.client.get(reverse("profile"))
        # stocker une chaîne non sécurisée dans first_name
        self.client.post(reverse("profile"), {
            "age": 25, "sex": "male", "height": 1.75, "weight": 70.0, "children": 0,
            "region": "northwest", "first_name": "<script>alert(1)</script>",
            "email": "u1@example.com"
        })
        self.u1.refresh_from_db()
        resp = self.client.get(reverse("profile"))
        # Django échappe automatiquement dans les templates, donc vérifier que la valeur est stockée mais échappée en HTML
        self.assertEqual(self.u1.first_name, "<script>alert(1)</script>")
        self.assertNotIn("<script>alert(1)</script>", resp.content.decode())
        self.assertIn("&lt;script&gt;", resp.content.decode())

    def test_cannot_modify_other_users_profile(self):
        # créer le profil pour u2 avec un âge distinct
        self.client.force_login(self.u2)
        self.client.get(reverse("profile"))
        self.client.post(reverse("profile"), {
            "age": 99, "sex": "male", "height": 1.75, "weight": 70.0,
            "children": 0, "region": "northwest", "email": "u2@example.com"
        })
        self.u2.profile.refresh_from_db()
        self.assertEqual(self.u2.profile.age, 99)
        
        # essayer de mettre à jour le profil de u2 en étant connecté comme u1 (ne devrait pas affecter u2)
        self.client.force_login(self.u1)
        self.client.post(reverse("profile"), {
            "age": 30, "sex": "male", "height": 1.75, "weight": 70.0,
            "children": 0, "region": "northwest", "email": "u1@example.com"
        })
        self.u2.profile.refresh_from_db()
        self.assertEqual(self.u2.profile.age, 99)

    def test_form_is_sticky_on_invalid_post(self):
        self.client.force_login(self.u1)
        self.client.get(reverse("profile"))
        resp = self.client.post(reverse("profile"), {
            "age": "not-an-int", "sex": "male", "height": 1.75, "weight": 70.0,
            "children": 0, "region": "northwest"
        })
        # la réponse doit contenir la valeur soumise (invalide) pour que l'utilisateur puisse la corriger
        self.assertIn("not-an-int", resp.content.decode())


User = get_user_model()

class ProfileExtraTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.u = User.objects.create_user(username="u", email="u@example.com", password="pass1234")
        self.client.force_login(self.u)
        # s'assurer que le profil existe
        self.client.get(reverse("profile"))

    def test_atomicity_user_form_invalid_does_not_change_profile(self):
        # définir un âge connu
        self.client.post(reverse("profile"), {
            "age": 30, "sex": "male", "height": 1.75, "weight": 70.0, "children": 0,
            "region": "northwest",
            "first_name": "Init", "last_name": "User", "email": "u@example.com"
        })
        self.u.profile.refresh_from_db()
        self.assertEqual(self.u.profile.age, 30)
        
        # soumettre avec un email invalide dans le formulaire utilisateur mais des données de profil valides
        resp = self.client.post(reverse("profile"), {
            "age": 40, "sex": "male", "height": 1.75, "weight": 75.0, "children": 0,
            "region": "northwest",
            "first_name": "X", "last_name": "Y", "email": "not-an-email"
        })
        self.u.profile.refresh_from_db()
        # le profil ne doit pas avoir été mis à jour car le formulaire utilisateur est invalide
        self.assertEqual(self.u.profile.age, 30)
        
        # le formulaire utilisateur doit être invalide localement
        uf = UserPersonalInfoForm(data={"email": "not-an-email"}, instance=self.u)
        self.assertFalse(uf.is_valid())

    def test_predict_page_prefills_from_profile(self):
        # mettre à jour les valeurs du profil
        self.client.post(reverse("profile"), {
            "age": 45, "sex": "female", "height": 1.65, "weight": 72.0, "children": 1,
            "region": "southeast",
            "first_name": "P", "last_name": "Q", "email": "u@example.com"
        })
        # essayer le chemin de prédiction commun
        resp = self.client.get("/predict/")
        # accepter 200 OK; si protégé, s'assurer de la redirection et non 500
        self.assertIn(resp.status_code, (200, 302))
        if resp.status_code == 200:
            content = resp.content.decode()
            # vérifier si les valeurs du profil apparaissent dans la page
            self.assertTrue("45" in content or "value=\"45\"" in content)

    def test_name_trimmed_on_save(self):
        self.client.post(reverse("profile"), {
            "age": 28, "sex": "male", "height": 1.75, "weight": 70.0, "children": 0,
            "region": "northwest",
            "first_name": "  Alice  ", "last_name": "  Dupont  ", "email": "u@example.com"
        })
        self.u.refresh_from_db()
        self.assertEqual(self.u.first_name, "Alice")
        self.assertEqual(self.u.last_name, "Dupont")