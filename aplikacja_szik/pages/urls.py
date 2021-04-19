# pages/urls.py
from django.urls import path, include
from . import views
from .views import HomeView


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', views.about, name='about'),
]
