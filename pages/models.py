from django.conf import settings
from django.db import models
from django.shortcuts import reverse


# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    discountPrice = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    description = models.TextField()
    image = models.ImageField(blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("pages:product", kwargs={
            "pk": self.pk

        })

    def get_add_to_cart_url(self):
        return reverse("pages:add-to-cart", kwargs={
            "pk": self.pk
        })

    def get_remove_from_cart_url(self):
        return reverse("pages:remove-from-cart", kwargs={
            "pk": self.pk
        })


class OrderLine(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class Order(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.ManyToManyField(OrderLine)
    orderDate = models.DateTimeField()
    ordered = models.BooleanField(default=False)
