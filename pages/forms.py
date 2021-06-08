# django
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
# third party
from db_file_storage.form_widgets import DBAdminClearableFileInput
# project
from .models import Product, SzikPoint, Invoice, UserProfile, UserType
from .username_validators import validate_username

from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


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
    username = forms.CharField(label='Login',
                               required=True,
                               min_length=8, validators=[validate_username],
                               widget=forms.TextInput(attrs={'placeholder': 'Login'}))
    email = forms.EmailField(label='E-mail',
                             required=True,
                             widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    password1 = forms.CharField(label='Hasło',
                                required=True,
                                widget=forms.PasswordInput(attrs={'placeholder': 'Hasło'}))
    password2 = forms.CharField(label='Powtórz hasło',
                                required=True,
                                widget=forms.PasswordInput(attrs={'placeholder': 'Powtórz hasło'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class CreateProfileForm(forms.ModelForm):
    user_type = forms.ModelChoiceField(label='Typ użytkownika', queryset=UserType.objects.all(), empty_label=None)

    class Meta:
        model = UserProfile
        fields = ['user_type']


PAYMENT = (
    ('B', 'BLIK'),
    ('V', 'karta VISA'),
    ('A', 'Apple Pay'),
    ('G', 'Google Pay'),
    ('P', 'PayPal')
)


class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))
    country = CountryField(blank_label='(wybierz kraj)').formfield(widget=CountrySelectWidget(attrs={
        'class': 'custom-select d-block w-100'
    }))
    zip_code = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT)
