# Django imports
from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver

# our imports
from django_countries.fields import CountryField


class SzikPointPhoto(models.Model):
    bytes = models.TextField()
    filename = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=50)


class SzikPoint(models.Model):
    city = models.CharField(max_length=30)
    street_address = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    telephone = models.CharField(max_length=9)
    photo = models.ImageField(upload_to='pages.SzikPointPhoto/bytes/filename/mimetype', blank=True, null=True)
    map_latitude = models.FloatField()
    map_longitude = models.FloatField()

    class Meta:
        verbose_name = "Punkt SZiK"
        verbose_name_plural = "Punkty SZiK"

    def __str__(self):
        return f"{self.street_address}, {self.postal_code} {self.city}"


class Category(models.Model):
    name = models.CharField(max_length=50)
    parent_category = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name = "Kategoria"
        verbose_name_plural = "Kategorie"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        url = reverse("pages:home")
        return f'{url}?&category={self.pk}'

    def get_subcategories(self):
        return Category.objects.filter(parent_category_id=self.pk)


class ProductImage(models.Model):
    bytes = models.TextField()
    filename = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=50)


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    discount = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    description = models.TextField()
    image = models.ImageField(upload_to='pages.ProductImage/bytes/filename/mimetype', blank=True, null=True)
    attributes = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name = "Produkt"
        verbose_name_plural = "Produkty"

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
        return self.category.name

    def get_discount(self):
        if self.discount:
            return self.price - self.discount
        else:
            return 0.0

    def get_discount_price(self):
        if self.discount:
            return self.discount
        return self.price


class ProductQuantity(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    point = models.ForeignKey(SzikPoint, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)


class InvoiceFile(models.Model):
    bytes = models.TextField()
    filename = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=50)


class Order(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # user_id
    payment_method = models.CharField(max_length=60, default="card")
    order_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    invoice_file = models.FileField(upload_to='pages.InvoiceFile/bytes/filename/mimetype', blank=True, null=True)

    class Meta:
        verbose_name = "Zamówienie"
        verbose_name_plural = "Zamówienia"

    def get_total_price(self):
        total = 0
        for order_line in self.order_lines.all():
            total += order_line.get_final_price()
        return total


class OrderLine(models.Model):
    order = models.ForeignKey(Order, related_name='order_lines', on_delete=models.CASCADE)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_lines', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        verbose_name = "Pozycja na zamówieniu"
        verbose_name_plural = "Pozycje na zamówieniu"

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_total_item_price(self):
        return self.quantity * self.product.price

    def get_discount_item_price(self):
        return self.quantity * self.product.get_discount_price()

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_discount_item_price()

    def get_final_price(self):
        if self.product.discount:
            return self.get_discount_item_price()
        return self.get_total_item_price()


class CheckoutAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip_code = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return self.user.username


class UserType(models.Model):
    name = models.CharField(max_length=20, null=False)

    class Meta:
        verbose_name = "Typ użytkownika"
        verbose_name_plural = "Typy użytkowników"

    def __str__(self):
        return self.name


class Profile(models.Model):
    user_id = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user_type = models.ForeignKey(UserType, null=True, on_delete=models.CASCADE)
    telephone = models.CharField(max_length=9, null=True)
    city = models.CharField(max_length=30, null=True)
    street_address = models.CharField(max_length=50, null=True)
    postal_code = models.CharField(max_length=20, null=True)

    def __str__(self):
        return str(self.user_id)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user_id=instance)
    instance.profile.save()


class VinNumber(models.Model):
    user_id = models.ForeignKey(Profile, on_delete=models.CASCADE)
    vin = models.CharField(max_length=17)

    class Meta:
        verbose_name = "Numer VIN"
        verbose_name_plural = "Numery VIN"

    def __str__(self):
        return self.vin
