from django.urls import path
from .views import home

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
]
