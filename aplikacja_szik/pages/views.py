# pages/views.py
from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    return render(request, 'pages/home.html', {'title': 'Home'})


def about(request):
    return HttpResponse('Projekt grupowy z Inżynierii Oprogramowania.')
