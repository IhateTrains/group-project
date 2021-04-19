# pages/views.py
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView
from .models import Product, Order, OrderLine


class HomeView(ListView):
    model = Product
    template_name = "pages/home.html"


def about(request):
    return HttpResponse('Projekt grupowy z Inżynierii Oprogramowania.')
