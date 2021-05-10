# django
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
# third party
from db_file_storage.form_widgets import DBAdminClearableFileInput
# project
from .models import Product, SzikPoint, Invoice


class ProductAdminForm(forms.ModelForm):
    class Meta(object):
        model = Product
        exclude = []
        widgets = {
            'index': DBAdminClearableFileInput,
            'pages': DBAdminClearableFileInput,
            'cover': DBAdminClearableFileInput,
        }


class SzikPointAdminForm(forms.ModelForm):
    class Meta(object):
        model = SzikPoint
        exclude = []
        widgets = {
            'index': DBAdminClearableFileInput,
            'pages': DBAdminClearableFileInput,
            'cover': DBAdminClearableFileInput,
        }


class InvoiceAdminForm(forms.ModelForm):
    class Meta(object):
        model = Invoice
        exclude = []
        widgets = {
            'index': DBAdminClearableFileInput,
            'pages': DBAdminClearableFileInput,
            'cover': DBAdminClearableFileInput,
        }

class CreateUserForm(UserCreationForm):
    username = forms.CharField(label='Login', required=True, min_length=8, widget=forms.TextInput(attrs={'placeholder': 'Login'}))
    email = forms.EmailField(label='E-mail', required=True, widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    password1 = forms.CharField(label='Haslo', required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Hasło'}))
    password2 = forms.CharField(label='Powtórz hasło', required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Powtórz hasło'}))
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']