from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

User = get_user_model()


class LoginViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="TestPassword123"
        )

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_login_success(self):
        """Un utilisateur valide peut se connecter."""
        response = self.client.post(
            reverse('login'),
            {
                "username": "testuser",
                "password": "TestPassword123"
            },
            follow=True
        )

        # Utilisateur bien connecté
        self.assertTrue(response.context["user"].is_authenticated)

        # Nouvelle redirection réelle : /profile/
        self.assertEqual(response.redirect_chain[-1][0], "/profile/")

        # Vérification du message de succès
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Connexion réussie" in str(m) for m in messages))

    def test_login_fail_wrong_password(self):
        """Le login doit échouer avec un mauvais mot de passe."""
        response = self.client.post(
            reverse('login'),
            {"username": "testuser", "password": "wrongpass"}
        )

        self.assertFalse(response.context["user"].is_authenticated)
        self.assertEqual(response.status_code, 200)

        # Vérifie un extrait robuste du message FR
        self.assertContains(response, "mot de passe valides")
