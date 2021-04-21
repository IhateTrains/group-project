from django.conf import settings
from django.db import models
from django.shortcuts import reverse


# Create your models here.

class SzikPoint(models.Model):
    city = models.ImageField(max_length=30)
    streetAddress = models.ImageField(max_length=50)
    postalCode = models.ImageField(max_length=20)
    telephone = models.CharField(max_length=9)
    photo = models.ImageField(blank=True, null=True)


class Category(models.Model):
    name = models.CharField(max_length=50)


class Product(models.Model):
    categoryID = models.ForeignKey(Category, on_delete=models.CASCADE)
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


class ProductQuantity(models.Model):
    productID = models.ForeignKey(Product, on_delete=models.CASCADE)
    pointID = models.ForeignKey(SzikPoint, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)


class OrderLine(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # userID
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)  # orderStatus

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class Order(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # userID
    paymentMethod = models.CharField(max_length=60)
    products = models.ManyToManyField(OrderLine)
    orderDate = models.DateTimeField()
    ordered = models.BooleanField(default=False)


class UserProfile(models.Model):
    userID = models.OneToOneField(settings.AUTH_USER_MODEL)
    telephone = models.CharField(max_length=9)
    city = models.ImageField(max_length=30)
    streetAddress = models.ImageField(max_length=50)
    postalCode = models.ImageField(max_length=20)


class UserType(models.Model):
    name = models.CharField(max_length=20, null=False)


class VinNumber(models.Model):
    userID = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    vin = models.CharField(max_length=17)
