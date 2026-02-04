from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Prediction
from profiles.models import Profile

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
# """Tests pour les vues""" 
    
    def setUp(self):
    #creer un utilisateur et un profil
        self.user=CustomUser.objects.create_user(
            username='testuser',
            password='password123'
        )

        self.profile = Profile.objects.create(
            user = self.user,
            age=30,
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

    # def test_view_without_profile(self):
    #     #Test : vue redirige vers profil si pas de profil
    #     user_no_profile = CustomUser.objects.create_user(
    #         username='noprofile',
    #         password='password123'
    #     )
    #     self.client.login(username='noprofile', password='testpass123')
    #     response = self.client.get(self.predict_url)
        
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, 'Compléter mon profil')
