from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Prediction

CustomUser = get_user_model()

class PredictionModelsTest(TestCase):
    #Tests pour les modèles

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