from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Prediction
from profiles.models import Profile
from unittest.mock import patch
import pandas as pd


CustomUser = get_user_model()

class PredictionModelsTest(TestCase):
    """Tests pour les modèles"""

    def setUp(self):
        #création d'utilisateur et prédiction pour faire les tests
        self.user= CustomUser.objects.create_user(
            username='testuser',
            password='password123'
        )
        
        self.prediction = Prediction.objects.create(
            user = self.user,
            predicted_charge = 1234.56
        )
    
    def test_prediction_creation(self):
        #test creation prediction
        self.assertEqual(self.prediction.user, self.user)
        self.assertEqual(self.prediction.predicted_charge, 1234.56)
        self.assertIsNotNone(self.prediction.created_at)
    
    def test_prediction_str(self):
        #test pour la methode str
        prediction_str = str(self.prediction)
        self.assertIn('testuser', prediction_str)
        self.assertIn('1234.56', prediction_str)

    def test_prediction_ordering(self):
        #voir si les prediction sont ordonées par la plus récente
        prediction2= Prediction.objects.create(
            user = self.user,
            predicted_charge = 7890.12
        )

        #verifier si la 2eme est la prémière
        predictions = Prediction.objects.filter(user=self.user)
        self.assertEqual(predictions.first(),prediction2)
        self.assertEqual(predictions.last(), self.prediction)
    
    def test_prediction_cascade_delete(self):
        #verification si prédiction suprimé si l'utilisateur est supprimé
        prediction_id= self.prediction.id
        self.user.delete()
        self.assertFalse(Prediction.objects.filter(id=prediction_id).exists())
    
    def test_prediction_related_name(self):
        #test pour voir si 'predictions' fcontionne (lien prediction - user)
        predictions = self.user.predictions.all()
        self.assertEqual(predictions.count(),1)
        self.assertEqual(predictions.first(), self.prediction)

class PredictView(TestCase):
    """Tests pour les vues""" 
    
    def setUp(self):
    #creer un utilisateur et un profil
        self.user=CustomUser.objects.create_user(
            username='testuser',
            password='password123'
        )

        self.profile = Profile.objects.create(
            user = self.user,
            age=15,
            sex='male',
            bmi=25.5,
            children=2,
            smoker=False,
            region='northwest'
        )
        self.predict_url = reverse('predict')
    
    def test_view_redirect_if_not_logged_in(self):
        #test redirecttion vers login si non authentifié
        response = self.client.get(self.predict_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_view_accessible_if_logged_in(self):
       # vue accessible si client authentifié
       self.client.login(username='testuser', password='password123')
       response = self.client.get(self.predict_url)
       self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
       #tester si vue utilise le bon template
       self.client.login(username='testuser', password='password123')
       response = self.client.get(self.predict_url)
       self.assertTemplateUsed(response, 'prediction/predict.html')
    
    def test_view_shows_profile_data(self):
        # tester l'affichage des données du profil
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.predict_url)
        
        self.assertContains(response, '30')  # Age
        self.assertContains(response, '25.5')  # BMI
        self.assertContains(response, '2')  # Children

    def test_view_without_profile(self):
        #Test : vue redirige vers profil si pas de profil
        user_no_profile = CustomUser.objects.create_user(
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

        data = {
            "age": 30,
            "sex": "male",
            "bmi": 25.5,
            "children": 1,
            "smoker": True,
            "region": "southwest"
        }

        response = self.client.post(self.predict_url, data)

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
        
        # POST pour créer prédiction
        form_data = {
            'age': 30,
            'sex': 'male',
            'bmi': 25.5,
            'children': 2,
            'smoker': False,
            'region': 'northwest'
        }
        self.client.post(self.predict_url, data=form_data)
        
        response = self.client.post(self.predict_url, data=form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '2345,67')

    @patch('prediction.views.model')
    def test_view_shows_history(self, mock_model):
        """Test : vue affiche l'historique des prédictions"""
        mock_model.predict.return_value = [1000.00]
        
        self.client.login(username='testuser', password='password123')
        
        form_data = {
            'age': 30,
            'sex': 'male',
            'bmi': 25.5,
            'children': 2,
            'smoker': False,
            'region': 'northwest'
        }
        # Créer 3 prédictions
        for i in range(3):
            self.client.post(self.predict_url, data=form_data)
        
        # Vérifier l'historique
        response = self.client.get(self.predict_url, data=form_data, follow=True)
        self.assertContains(response, 'Historique')
        predictions = Prediction.objects.filter(user=self.user)
        self.assertEqual(predictions.count(), 3)
    
    @patch('prediction.views.model')
    @patch('prediction.views.rmse', 100.0)
    def test_view_shows_rmse_conditionally(self, mock_model):
        """Test : vue affiche RMSE seulement si predicted_charge - rmse >= 1000"""
        self.client.login(username='testuser', password='password123')
        
        # Dados do formulário
        form_data = {
            'age': 30,
            'sex': 'male',
            'bmi': 25.5,
            'children': 2,
            'smoker': False,
            'region': 'northwest'
        }
        
        # Cas 1: Valeur haute (>1000) - doit afficher RMSE
        mock_model.predict.return_value = [2000.00]
        self.client.post(self.predict_url, data=form_data, follow=True)
        response = self.client.get(self.predict_url)
        self.assertContains(response, '±')
        
        # Cas 2: Valeur basse (<1000) - ne doit PAS afficher RMSE
        mock_model.predict.return_value = [900.00]
        self.client.post(self.predict_url, data=form_data, follow=True)
        response = self.client.get(self.predict_url)
        # La dernière prédiction est 900, donc pas de ±
        self.assertNotContains(response, '±')
        
    def test_view_context_contains_necessary_data(self):
        """Test : contexte contient les données nécessaires"""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.predict_url)
        
        self.assertIn('profile', response.context)
        self.assertIn('rmse', response.context)

# ==================== TESTS D'INTÉGRATION ====================

class PredictionIntegrationTest(TestCase):
    """Tests d'intégration pour le parcours complet"""
    
    def setUp(self):
        """Créer un client et un utilisateur avec profil"""
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='password123'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            age=35,
            sex='female',
            bmi=22.0,
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
        
        # 4. Faire une prédiction (POST) avec follow=True pour voir redirects
        form_data = {
            'age': 35,
            'sex': 'female',
            'bmi': 22.0,
            'children': 1,
            'smoker': True,
            'region': 'southeast'
        }
        
        # Faire POST avec follow=True
        response = self.client.post(self.predict_url, data=form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # 5. Vérifier que la prédiction a été créée
        self.assertTrue(Prediction.objects.filter(user=self.user).exists())
        prediction = Prediction.objects.get(user=self.user)
        self.assertEqual(prediction.predicted_charge, 3456.78)
        
        # 6. Vérifier que le résultat est affiché
        self.assertContains(response, '3456,78')

    
    @patch('prediction.views.model')
    def test_multiple_predictions_create_history(self, mock_model):
        """Test : plusieurs prédictions créent un historique"""
        mock_model.predict.return_value = [1500.00]
        
        self.client.login(username='testuser', password='password123')
        
        # Dados do formulário
        form_data = {
            'age': 35,
            'sex': 'female',
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

