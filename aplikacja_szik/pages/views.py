# pages/views.py
from django.shortcuts import render
from django.http import HttpResponse


def homePageView(request):
    return HttpResponse('<h2>Hello, World!</h2>')


def aboutView(request):
    return HttpResponse('Projekt grupowy z Inżynierii Oprogramowania.')
