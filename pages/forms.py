# django
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
# third party
from db_file_storage.form_widgets import DBAdminClearableFileInput
# project
from .models import Product, SzikPoint, Invoice, Profile, UserType, VinNumber
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
        model = Profile
        fields = ['user_type']


class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(label='Login',
                               required=False,
                               min_length=8, validators=[validate_username])
    email = forms.EmailField(label='E-mail',
                             required=False)
    first_name = forms.CharField(label='Imie',
                                 required=False)
    last_name = forms.CharField(label='Nazwisko',
                                 required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class UpdateProfileForm(forms.ModelForm):
    telephone = forms.CharField(label='Telefon', required=False, max_length=9)
    city = forms.CharField(label='Miasto', required=False, max_length=30)
    street_address = forms.CharField(label='Adres', required=False, max_length=50)
    postal_code = forms.CharField(label='Kod pocztowy', required=False, max_length=20)

    class Meta:
        model = Profile
        fields = ['telephone', 'city', 'street_address', 'postal_code']


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
