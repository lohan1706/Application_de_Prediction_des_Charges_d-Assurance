from django.db import models
from profiles.models import CustomUser

class Prediction(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    predicted_charge = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.predicted_charge}"
