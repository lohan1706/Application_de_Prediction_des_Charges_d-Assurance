from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Prediction
from profiles.models import Profile
from unittest.mock import patch
import pandas as pd


User = get_user_model()


# ==================== TESTS DES MODÈLES ====================

class PredictionModelsTest(TestCase):
    """Tests pour les modèles"""

    def setUp(self):
        """Création d'utilisateur et prédiction pour faire les tests"""
        self.user = User.objects.create_user(
            username='testuser',
            password='password123'
        )
        
        self.prediction = Prediction.objects.create(
            user=self.user,
            predicted_charge=1234.56
        )
    
    def test_prediction_creation(self):
        """Test création prediction"""
        self.assertEqual(self.prediction.user, self.user)
        self.assertEqual(self.prediction.predicted_charge, 1234.56)
        self.assertIsNotNone(self.prediction.created_at)
    
    def test_prediction_str(self):
        """Test pour la méthode str"""
        prediction_str = str(self.prediction)
        self.assertIn('testuser', prediction_str)
        self.assertIn('1234.56', prediction_str)

    def test_prediction_ordering(self):
        """Voir si les predictions sont ordonnées par la plus récente"""
        prediction2 = Prediction.objects.create(
            user=self.user,
            predicted_charge=7890.12
        )

        # Vérifier si la 2ème est la première
        predictions = Prediction.objects.filter(user=self.user)
        self.assertEqual(predictions.first(), prediction2)
        self.assertEqual(predictions.last(), self.prediction)
    
    def test_prediction_cascade_delete(self):
        """Vérification si prédiction supprimée si l'utilisateur est supprimé"""
        prediction_id = self.prediction.id
        self.user.delete()
        self.assertFalse(Prediction.objects.filter(id=prediction_id).exists())
    
    def test_prediction_related_name(self):
        """Test pour voir si 'predictions' fonctionne (lien prediction - user)"""
        predictions = self.user.predictions.all()
        self.assertEqual(predictions.count(), 1)
        self.assertEqual(predictions.first(), self.prediction)


# ==================== TESTS DES VUES ====================

class PredictViewTest(TestCase):
    """Tests pour les vues""" 
    
    def setUp(self):
        """Créer un utilisateur et un profil"""
        self.user = User.objects.create_user(
            username='testuser',
            password='password123'
        )

        self.profile = Profile.objects.create(
            user=self.user,
            age=30,  # ✅ Corrigé: >= 18
            sex='male',
            height=1.75,  # ✅ Ajouté
            weight=78.0,  # ✅ Ajouté
            # bmi sera calculé automatiquement = 25.5
            children=2,
            smoker=False,
            region='northwest'
        )
        self.predict_url = reverse('predict')
    
    def test_view_redirect_if_not_logged_in(self):
        """Test redirection vers login si non authentifié"""
        response = self.client.get(self.predict_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_view_accessible_if_logged_in(self):
        """Vue accessible si client authentifié"""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.predict_url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Tester si vue utilise le bon template"""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.predict_url)
        self.assertTemplateUsed(response, 'prediction/predict.html')
    
    def test_view_shows_profile_data(self):
        """Tester l'affichage des données du profil"""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.predict_url)
        
        self.assertContains(response, '30')  # Age
        self.assertContains(response, '2')  # Children

    def test_view_without_profile(self):
        """Test : vue redirige vers profil si pas de profil"""
        user_no_profile = User.objects.create_user(
            username='noprofile',
            password='password123'
        )
        self.client.login(username='noprofile', password='password123')
        response = self.client.get(self.predict_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Compléter mon profil')

    @patch('prediction.views.model')
    def test_view_creates_prediction_on_post(self, mock_model):
        """Test : vue crée une prédiction avec POST"""
        mock_model.predict.return_value = [1234.56]

        self.client.login(username='testuser', password='password123')

        form_data = {
            'age': 30,
            'sex': 'male',
            'height': 1.75,  # ✅ Ajouté
            'weight': 78.0,  # ✅ Ajouté
            'bmi': 25.5,
            'children': 1,
            'smoker': True,
            'region': 'southwest'
        }

        response = self.client.post(self.predict_url, data=form_data, follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            Prediction.objects.filter(user=self.user).exists()
        )

        prediction = Prediction.objects.get(user=self.user)
        self.assertEqual(prediction.predicted_charge, 1234.56)

    @patch('prediction.views.model')
    def test_view_shows_prediction_result(self, mock_model):
        """Test : vue affiche le résultat de la prédiction"""
        mock_model.predict.return_value = [2345.67]
        
        self.client.login(username='testuser', password='password123')
        
        form_data = {
            'age': 30,
            'sex': 'male',
            'height': 1.75,  # ✅ Ajouté
            'weight': 78.0,  # ✅ Ajouté
            'bmi': 25.5,
            'children': 2,
            'smoker': False,
            'region': 'northwest'
        }
        
        response = self.client.post(self.predict_url, data=form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '2345')

    @patch('prediction.views.model')
    def test_view_shows_history(self, mock_model):
        """Test : vue affiche l'historique des prédictions"""
        mock_model.predict.return_value = [1000.00]
        
        self.client.login(username='testuser', password='password123')
        
        form_data = {
            'age': 30,
            'sex': 'male',
            'height': 1.75,  # ✅ Ajouté
            'weight': 78.0,  # ✅ Ajouté
            'bmi': 25.5,
            'children': 2,
            'smoker': False,
            'region': 'northwest'
        }
        
        # Créer 3 prédictions
        for i in range(3):
            self.client.post(self.predict_url, data=form_data, follow=True)
        
        # Vérifier l'historique
        response = self.client.get(self.predict_url)
        self.assertContains(response, 'Historique')
        predictions = Prediction.objects.filter(user=self.user)
        self.assertEqual(predictions.count(), 3)
    
    @patch('prediction.views.model')
    @patch('prediction.views.rmse', 100.0)
    def test_view_shows_rmse_conditionally(self, mock_model):
        """Test : vue affiche RMSE seulement si predicted_charge - rmse >= 1000"""
        self.client.login(username='testuser', password='password123')
        
        form_data = {
            'age': 30,
            'sex': 'male',
            'height': 1.75,  # ✅ Ajouté
            'weight': 78.0,  # ✅ Ajouté
            'bmi': 25.5,
            'children': 2,
            'smoker': False,
            'region': 'northwest'
        }
        
        # Cas 1: Valeur haute (>1000) - doit afficher RMSE
        mock_model.predict.return_value = [2000.00]
        response = self.client.post(self.predict_url, data=form_data, follow=True)
        self.assertContains(response, '±')
        
        # Cas 2: Valeur basse (<1000) - ne doit PAS afficher RMSE
        mock_model.predict.return_value = [900.00]
        response = self.client.post(self.predict_url, data=form_data, follow=True)
        self.assertNotContains(response, '±')
        
    def test_view_context_contains_necessary_data(self):
        """Test : contexte contient les données nécessaires"""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.predict_url)
        
        self.assertIn('profile', response.context)
        self.assertIn('rmse', response.context)
    
    # ==================== TESTS DE VALIDATION ====================
    
    @patch('prediction.views.model')
    def test_age_below_18_rejected(self, mock_model):
        """Test : âge inférieur à 18 ans est rejeté"""
        mock_model.predict.return_value = [1000.00]
        
        self.client.login(username='testuser', password='password123')
        
        form_data = {
            'age': 15,  # ❌ Invalide
            'sex': 'male',
            'height': 1.75,
            'weight': 78.0,
            'bmi': 25.5,
            'children': 2,
            'smoker': False,
            'region': 'northwest'
        }
        
        response = self.client.post(self.predict_url, data=form_data, follow=True)
        
        # Pas de prédiction créée
        self.assertEqual(Prediction.objects.filter(user=self.user).count(), 0)
        
        # Message d'erreur affiché
        self.assertContains(response, "Veuillez corriger les erreurs")
    
    
    @patch('prediction.views.model')
    def test_age_18_accepted(self, mock_model):
        """Test : âge exactement 18 ans est accepté"""
        mock_model.predict.return_value = [1000.00]
        
        self.client.login(username='testuser', password='password123')
        
        form_data = {
            'age': 18,  # ✅ Valide (minimum)
            'sex': 'male',
            'height': 1.75,
            'weight': 78.0,
            'bmi': 25.5,
            'children': 2,
            'smoker': False,
            'region': 'northwest'
        }
        
        response = self.client.post(self.predict_url, data=form_data, follow=True)
        
        # Prédiction créée
        self.assertEqual(Prediction.objects.filter(user=self.user).count(), 1)
        self.assertContains(response, "Profil mis à jour et prédiction effectuée")
    
    
    @patch('prediction.views.model')
    def test_negative_children_rejected(self, mock_model):
        """Test : nombre d'enfants négatif est rejeté"""
        mock_model.predict.return_value = [1000.00]
        
        self.client.login(username='testuser', password='password123')
        
        form_data = {
            'age': 30,
            'sex': 'male',
            'height': 1.75,
            'weight': 78.0,
            'bmi': 25.5,
            'children': -1,  # ❌ Invalide
            'smoker': False,
            'region': 'northwest'
        }
        
        response = self.client.post(self.predict_url, data=form_data, follow=True)
        
        # Pas de prédiction créée
        self.assertEqual(Prediction.objects.filter(user=self.user).count(), 0)
        self.assertContains(response, "Veuillez corriger les erreurs")
    
    
    @patch('prediction.views.model')
    def test_zero_children_accepted(self, mock_model):
        """Test : zéro enfant est accepté"""
        mock_model.predict.return_value = [1000.00]
        
        self.client.login(username='testuser', password='password123')
        
        form_data = {
            'age': 30,
            'sex': 'male',
            'height': 1.75,
            'weight': 78.0,
            'bmi': 25.5,
            'children': 0,  # ✅ Valide (minimum)
            'smoker': False,
            'region': 'northwest'
        }
        
        response = self.client.post(self.predict_url, data=form_data, follow=True)
        
        # Prédiction créée
        self.assertEqual(Prediction.objects.filter(user=self.user).count(), 1)
        self.assertContains(response, "Profil mis à jour et prédiction effectuée")
    
    
    @patch('prediction.views.model')
    def test_negative_height_rejected(self, mock_model):
        """Test : taille négative est rejetée"""
        mock_model.predict.return_value = [1000.00]
        
        self.client.login(username='testuser', password='password123')
        
        form_data = {
            'age': 30,
            'sex': 'male',
            'height': -1.75,  # ❌ Invalide
            'weight': 78.0,
            'bmi': 25.5,
            'children': 2,
            'smoker': False,
            'region': 'northwest'
        }
        
        response = self.client.post(self.predict_url, data=form_data, follow=True)
        
        # Pas de prédiction créée
        self.assertEqual(Prediction.objects.filter(user=self.user).count(), 0)
        self.assertContains(response, "Veuillez corriger les erreurs")


# ==================== TESTS D'INTÉGRATION ====================

class PredictionIntegrationTest(TestCase):
    """Tests d'intégration pour le parcours complet"""
    
    def setUp(self):
        """Créer un client et un utilisateur avec profil"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='password123'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            age=35,
            sex='female',
            height=1.68,  # ✅ Ajouté
            weight=62.0,  # ✅ Ajouté
            # bmi será calculado = 22.0
            children=1,
            smoker=True,
            region='southeast'
        )
        self.predict_url = reverse('predict')
        
    @patch('prediction.views.model')
    def test_complete_prediction_flow(self, mock_model):
        """Test : flux complet de prédiction"""
        mock_model.predict.return_value = [3456.78]
        
        # 1. Login
        self.client.login(username='testuser', password='password123')
        
        # 2. Accéder à la page predict
        response = self.client.get(self.predict_url)
        self.assertEqual(response.status_code, 200)
        
        # 3. Vérifier que les données du profil sont affichées
        self.assertContains(response, '35')  # Age
        
        # 4. Faire une prédiction (POST)
        form_data = {
            'age': 35,
            'sex': 'female',
            'height': 1.68,  # ✅ Ajouté
            'weight': 62.0,  # ✅ Ajouté
            'bmi': 22.0,
            'children': 1,
            'smoker': True,
            'region': 'southeast'
        }
        
        response = self.client.post(self.predict_url, data=form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # 5. Vérifier que la prédiction a été créée
        self.assertTrue(Prediction.objects.filter(user=self.user).exists())
        prediction = Prediction.objects.get(user=self.user)
        self.assertEqual(prediction.predicted_charge, 3456.78)
        
        # 6. Vérifier que le résultat est affiché
        self.assertContains(response, '3456')

    
    @patch('prediction.views.model')
    def test_multiple_predictions_create_history(self, mock_model):
        """Test : plusieurs prédictions créent un historique"""
        mock_model.predict.return_value = [1500.00]
        
        self.client.login(username='testuser', password='password123')
        
        form_data = {
            'age': 35,
            'sex': 'female',
            'height': 1.68,  # ✅ Ajouté
            'weight': 62.0,  # ✅ Ajouté
            'bmi': 22.0,
            'children': 1,
            'smoker': True,
            'region': 'southeast'
        }
        
        # Créer 5 prédictions
        for i in range(5):
            self.client.post(self.predict_url, data=form_data, follow=True)
        
        # Vérifier que 5 prédictions existent
        predictions = Prediction.objects.filter(user=self.user)
        self.assertEqual(predictions.count(), 5)
        
        # Vérifier que l'historique est affiché
        response = self.client.get(self.predict_url)
        self.assertContains(response, 'Historique')


# ==================== TESTS DES SERVICES ====================

class PredictionServicesTest(TestCase):
    """Tests pour les services (model ML, rmse)"""
    
    def test_model_import(self):
        """Test : le modèle ML peut être importé"""
        try:
            from prediction.services import model
            self.assertIsNotNone(model)
        except Exception as e:
            self.fail(f"Impossible d'importer le modèle: {e}")
    
    def test_rmse_import(self):
        """Test : le RMSE peut être importé"""
        try:
            from prediction.services import rmse
            self.assertIsNotNone(rmse)
            self.assertIsInstance(rmse, (int, float))
        except Exception as e:
            self.fail(f"Impossible d'importer le RMSE: {e}")

    @patch('prediction.services.model')
    def test_model_predict_returns_numeric(self, mock_model):
        """Test : le modèle retourne une valeur numérique"""
        mock_model.predict.return_value = [1234.56]
        
        from prediction.services import model
        
        # Données test
        data = pd.DataFrame([{
            'age': 30,
            'sex': 'male',
            'bmi': 25.5,
            'children': 2,
            'smoker': 'no',
            'region': 'northwest'
        }])
        
        result = model.predict(data)[0]
        self.assertIsInstance(result, (int, float))