from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.


class SzikPointPhoto(models.Model):
    bytes = models.TextField()
    filename = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=50)


class SzikPoint(models.Model):
    city = models.CharField(max_length=30)
    streetAddress = models.CharField(max_length=50)
    postalCode = models.CharField(max_length=20)
    telephone = models.CharField(max_length=9)
    photo = models.ImageField(upload_to='pages.SzikPointPhoto/bytes/filename/mimetype', blank=True, null=True)
    mapLatitude = models.DecimalField()
    mapLongitude = models.DecimalField()

    def __str__(self):
        return f"{self.streetAddress}, {self.postalCode} {self.city}"


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    bytes = models.TextField()
    filename = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=50)


class Product(models.Model):
    categoryID = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    discountPrice = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    description = models.TextField()
    image = models.ImageField(upload_to='pages.ProductImage/bytes/filename/mimetype', blank=True, null=True)

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

    def get_category_display(self):
        return self.categoryID.name


class ProductQuantity(models.Model):
    productID = models.ForeignKey(Product, on_delete=models.CASCADE)
    pointID = models.ForeignKey(SzikPoint, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)


class OrderLine(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # userID
    product = models.ForeignKey(Product, related_name ='product_OrderLine', on_delete=models.CASCADE)   #related_name=...
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)  # orderStatus

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_total_item_price(self):
        return self.quantity * self.product.price

    def get_discount_item_price(self):
        return self.quantity * self.product.discountPrice

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_discount_item_price()

    def get_final_price(self):
        if self.product.discountPrice:
            return self.get_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # userID
    paymentMethod = models.CharField(max_length=60, default="card")
    products = models.ManyToManyField(OrderLine)
    orderDate = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def get_total_price(self):
        total = 0
        for order_item in self.products.all():
            total += order_item.get_final_price()
        return total


class UserType(models.Model):
    name = models.CharField(max_length=20, null=False)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    userID = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    userType = models.ForeignKey(UserType, null=True,  on_delete=models.CASCADE)
    telephone = models.CharField(max_length=9)
    city = models.CharField(max_length=30)
    streetAddress = models.CharField(max_length=50)
    postalCode = models.CharField(max_length=20)

    def __str__(self):
        return str(self.userID)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(userID=instance)
    instance.userprofile.save()


class VinNumber(models.Model):
    userID = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    vin = models.CharField(max_length=17)

    def __str__(self):
        return self.vin


class InvoiceFile(models.Model):
    bytes = models.TextField()
    filename = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=50)


class Invoice(models.Model):
    orderID = models.ForeignKey(Order, on_delete=models.CASCADE)
    pdfFile = models.FileField(upload_to='pages.InvoiceFile/bytes/filename/mimetype', blank=True, null=True)
