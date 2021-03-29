# pages/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('', views.homePageView, name='home'),
    path('about/', views.aboutView, name='about'),
]
