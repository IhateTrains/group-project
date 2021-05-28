from django.db import models

from oscar.apps.catalogue.abstract_models import AbstractProductImage


class ProductImageStorage(models.Model):
    bytes = models.TextField()
    filename = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=50)


class ProductImage(AbstractProductImage):
    original = models.ImageField(upload_to='catalogue.ProductImageStorage/bytes/filename/mimetype',
                                 blank=True,
                                 null=True
    )


from oscar.apps.catalogue.models import *