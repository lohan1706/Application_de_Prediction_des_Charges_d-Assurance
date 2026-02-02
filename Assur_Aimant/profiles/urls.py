from django.urls import path
from .views import ProfileView, PredictionView

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('prediction/', PredictionView.as_view(), name='prediction'),
]