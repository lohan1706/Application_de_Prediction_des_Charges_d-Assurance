from django.db import models
from django.contrib.auth.models import AbstractUser

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

    age = models.IntegerField()
    sex = models.CharField(max_length=10)
    bmi = models.FloatField()
    children = models.IntegerField()
    smoker = models.BooleanField()
    region = models.CharField(max_length=50)

    def __str__(self):
        return self.user.username
    
