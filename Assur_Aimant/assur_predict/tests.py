from django.test import TestCase
from django.contrib.auth import get_user_model
from django.template import Template, Context
from django.urls import reverse
from unittest.mock import patch
from prediction.models import Prediction



User = get_user_model()

class HomeTemplateTests(TestCase):
    def test_home_page_renders_and_uses_home_template(self):
        resp = self.client.get("/")  # page d'accueil
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "assur_predict/home.html")
        content = resp.content.decode()
        # éléments présentiels attendus dans base/home
        self.assertIn("AssurPredict", content)
        self.assertIn("/static/css/dist/styles.css", content)

    def test_home_shows_login_link_when_anonymous(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("/login/", resp.content.decode())

    def test_home_shows_username_and_logout_when_logged_in(self):
        user = User.objects.create_user(username="alice", password="pass1234")
        self.client.login(username="alice", password="pass1234")
        resp = self.client.get("/")
        content = resp.content.decode()
        self.assertIn("alice", content)
        self.assertIn("/logout/", content)


class BaseTemplateBlockTests(TestCase):
    def test_base_template_accepts_content_block(self):
        # on étend base.html et on vérifie que le block content est rendu
        t = Template("{% extends 'base.html' %}{% block content %}UNIQUE_CONTENT{% endblock %}")
        rendered = t.render(Context({}))
        self.assertIn("UNIQUE_CONTENT", rendered)

    def test_base_contains_footer(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("<footer", resp.content.decode())    



User = get_user_model()

class EndToEndTests(TestCase):
    def test_signup_profile_and_predict_flow(self):
        # 1) Inscription (Signup)
        signup_data = {
            "username": "e2euser",
            "email": "e2e@example.com",
            "password1": "StrongPass123",
            "password2": "StrongPass123",
        }
        resp = self.client.post(reverse("signup"), signup_data, follow=True)
        self.assertEqual(resp.status_code, 200)
        user = User.objects.get(username="e2euser")

        # 2) Connexion (client.login utilise le backend d'authentification)
        logged = self.client.login(username="e2euser", password="StrongPass123")
        self.assertTrue(logged)

        # 3) Accéder au profil (profil créé lors du premier accès) et le mettre à jour
        resp = self.client.get(reverse("profile"))
        self.assertEqual(resp.status_code, 200)

        profile_post = {
            "age": 30,
            "sex": "male",
            "height": 1.75,
            "weight": 72.0,
            "children": 1,
            "smoker": "on",  # checkbox cochée
            "region": "northwest",
            "first_name": "End",
            "last_name": "ToEnd",
            "email": "e2euser@example.com",
        }
        resp = self.client.post(reverse("profile"), profile_post, follow=True)
        self.assertEqual(resp.status_code, 200)
        user.refresh_from_db()
        self.assertEqual(user.profile.age, 30)
        self.assertTrue(user.profile.smoker)
        # vérifier que le BMI a été calculé automatiquement
        expected_bmi = round(72.0 / (1.75 ** 2), 1)
        self.assertAlmostEqual(user.profile.bmi, expected_bmi, places=1)

        # 4) GET page predict -> le formulaire doit être pré-rempli (modifiable)
        resp = self.client.get(reverse("predict"))
        self.assertEqual(resp.status_code, 200)
        form = resp.context.get("form")
        self.assertIsNotNone(form)
        # les valeurs initiales viennent du profil
        self.assertEqual(form.initial.get("age"), 30)
        self.assertEqual(form.initial.get("height"), 1.75)
        self.assertEqual(form.initial.get("weight"), 72.0)

        class FakeModel:
            def predict(self, df):
                return [777.88]

        # Patcher l'objet réellement utilisé par la vue
        with patch("prediction.views.model", new=FakeModel()):
            predict_post = {
                "age": 35,
                "sex": "male",
                "height": 1.70,
                "weight": 72.3,
                "children": 1,
                "smoker": "",
                "region": "northwest",
            }
            resp = self.client.post(reverse("predict"), predict_post, follow=True)
            self.assertEqual(resp.status_code, 200)
            content = resp.content.decode()
            # vérifier que la prédiction apparaît dans le contenu (avec point ou virgule selon la locale)
            self.assertTrue("777.88" in content or "777,88" in content)
            # vérifier que la prédiction a été enregistrée en base de données
            pred = Prediction.objects.filter(user=user).last()
            self.assertIsNotNone(pred)
            self.assertAlmostEqual(pred.predicted_charge, 777.88, places=2)