from django.contrib import admin

from . import models

# Register your models here.
admin.site.register(models.SzikPoint)
admin.site.register(models.Category)
admin.site.register(models.Product)
admin.site.register(models.ProductQuantity)
admin.site.register(models.OrderLine)
admin.site.register(models.Order)
admin.site.register(models.UserProfile)
admin.site.register(models.UserType)
admin.site.register(models.VinNumber)
