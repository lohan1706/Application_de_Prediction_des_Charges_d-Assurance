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

class LogoutViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="logoutuser",
            password="LogoutPassword123"
        )

    def test_logout_redirects_home(self):
        """Un utilisateur connecté doit être déconnecté et redirigé vers login."""
        self.client.login(username="logoutuser", password="LogoutPassword123")

        # POST au lieu de GET si logout est POST
        response = self.client.post(reverse("logout"), follow=True)

        # utilisateur déconnecté
        self.assertFalse(response.wsgi_request.user.is_authenticated)

        # redirection finale vers /login/
        self.assertRedirects(response, reverse("login"))

        # message de déconnexion
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("déconnecté" in str(m) for m in messages))

    def test_logout_requires_login(self):
        """Si l'utilisateur n'est pas connecté, logout doit rediriger vers login."""
        response = self.client.post(reverse("logout"), follow=True)

        # redirection finale vers login
        self.assertRedirects(response, reverse("login"))


class PasswordHashingTest(TestCase):
    """Tests de hachage des mots de passe"""
    
    def test_password_is_hashed(self):
        """Test: le mot de passe est haché, pas en clair"""
        user = User.objects.create_user(
            username='testuser',
            password='plainpassword123'
        )
        
        # Le mot de passe NE doit PAS être en clair
        self.assertNotEqual(user.password, 'plainpassword123')
        
        # Le mot de passe doit commencer par l'algorithme
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))
    
    def test_password_verification_works(self):
        """Test: la vérification du mot de passe fonctionne"""
        user = User.objects.create_user(
            username='testuser',
            password='mypassword'
        )
        
        # Le bon mot de passe doit être accepté
        self.assertTrue(user.check_password('mypassword'))
        
        # Un mauvais mot de passe doit être rejeté
        self.assertFalse(user.check_password('wrongpassword'))

