from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import Profile


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
