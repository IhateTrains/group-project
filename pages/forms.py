# django
from django import forms
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
