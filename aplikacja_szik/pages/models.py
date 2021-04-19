from django.db import models
from django.conf import settings


# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.FloatField()
    description = models.TextField()

    def __str__(self):
        return self.name


class Order(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    orderDate = models.DateTimeField()


class OrderLine(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
