from django.db import models
from profiles.models import CustomUser

class Prediction(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='predictions')
    predicted_charge = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Prédiction"
        verbose_name_plural = "Prédictions"

    def __str__(self):
        return f"{self.user.username} - {self.predicted_charge:.2f}€ ({self.created_at.strftime('%d/%m/%Y')})"