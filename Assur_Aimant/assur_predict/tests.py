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



