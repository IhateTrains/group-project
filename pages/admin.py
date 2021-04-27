# Django
from django.contrib import admin
# project
from .forms import ProductAdminForm, SzikPointAdminForm, InvoiceAdminForm
from . import models

# Register your models here.
admin.site.register(models.Category)
admin.site.register(models.ProductQuantity)
admin.site.register(models.OrderLine)
admin.site.register(models.Order)
admin.site.register(models.UserProfile)
admin.site.register(models.UserType)
admin.site.register(models.VinNumber)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm


@admin.register(models.SzikPoint)
class SzikPointAdmin(admin.ModelAdmin):
    form = SzikPointAdminForm


@admin.register(models.Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    form = InvoiceAdminForm