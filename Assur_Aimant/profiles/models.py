from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

class CustomUser(AbstractUser):
    #     ROLE_CHOICES = [
    #     ("client", "Client"),
    #     ("advisor", "Advisor"),
    # ]

    # role = models.CharField(
    #     max_length=20,
    #     choices=ROLE_CHOICES,
    #     default="client"
    # )
    def __str__(self):
        return self.username

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    age = models.IntegerField(validators=[MinValueValidator(18)])
    sex = models.CharField(max_length=10)
    height = models.FloatField(help_text="Taille en mètres", validators=[MinValueValidator(0)])  # ajout de la taille
    weight = models.FloatField(help_text="Poids en kg", validators=[MinValueValidator(0)])       # ajout du poids
    bmi = models.FloatField(blank=True)                        # IMC calculé automatiquement
    children = models.IntegerField(validators=[MinValueValidator(0)])
    smoker = models.BooleanField()
    region = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        if self.height > 0 and self.weight > 0:
            self.bmi = round(self.weight / (self.height ** 2), 1)  # calcul automatique
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username
    
