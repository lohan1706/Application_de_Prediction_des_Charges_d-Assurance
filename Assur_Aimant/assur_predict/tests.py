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

def test_base_accepts_extra_head_and_scripts_blocks(self):
        head_t = Template("{% extends 'base.html' %}{% block extra_head %}MYHEAD{% endblock %}")
        self.assertIn("MYHEAD", head_t.render(Context({})))
        scripts_t = Template("{% extends 'base.html' %}{% block scripts %}MYSCRIPT{% endblock %}")
        self.assertIn("MYSCRIPT", scripts_t.render(Context({})))        



User = get_user_model()

class EndToEndTests(TestCase):
    def test_signup_profile_and_predict_flow(self):
        # 1) Signup
        signup_data = {
            "username": "e2euser",
            "email": "e2e@example.com",
            "password1": "StrongPass123",
            "password2": "StrongPass123",
        }
        resp = self.client.post(reverse("signup"), signup_data, follow=True)
        self.assertEqual(resp.status_code, 200)
        user = User.objects.get(username="e2euser")

        # 2) Login (client.login uses auth backend)
        logged = self.client.login(username="e2euser", password="StrongPass123")
        self.assertTrue(logged)

        # 3) Access profile (profile created on first access) and update it
        resp = self.client.get(reverse("profile"))
        self.assertEqual(resp.status_code, 200)

        profile_post = {
            "age": 30,
            "sex": "male",
            "bmi": 23.5,
            "children": 1,
            "smoker": "on",  # checked checkbox
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

        # 4) GET predict page -> form must be prefilled (editable)
        resp = self.client.get(reverse("predict"))
        self.assertEqual(resp.status_code, 200)
        form = resp.context.get("form")
        self.assertIsNotNone(form)
        # initial values come from profile
        self.assertEqual(form.initial.get("age"), 30)
        self.assertEqual(form.initial.get("bmi"), 23.5)

        class FakeModel:
            def predict(self, df):
                return [777.88]

        # Patch l'objet réellement utilisé par la vue
        with patch("prediction.views.model", new=FakeModel()):
            predict_post = {
                "age": 35,
                "sex": "male",
                "bmi": 25.0,
                "children": 1,
                "smoker": "",
                "region": "northwest",
            }
            resp = self.client.post(reverse("predict"), predict_post, follow=True)
            self.assertEqual(resp.status_code, 200)
            content = resp.content.decode()
            self.assertTrue("777.88" in content or "777,88" in content)
            pred = Prediction.objects.filter(user=user).last()
            self.assertIsNotNone(pred)
            self.assertAlmostEqual(pred.predicted_charge, 777.88, places=2)


