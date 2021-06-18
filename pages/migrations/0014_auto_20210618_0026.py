# Generated by Django 3.2.2 on 2021-06-17 22:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0013_rename_zip_checkoutaddress_zip_code'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'Kategoria', 'verbose_name_plural': 'Kategorie'},
        ),
        migrations.AlterModelOptions(
            name='invoice',
            options={'verbose_name': 'Faktura', 'verbose_name_plural': 'Faktury'},
        ),
        migrations.AlterModelOptions(
            name='order',
            options={'verbose_name': 'Zamówienie', 'verbose_name_plural': 'Zamówienia'},
        ),
        migrations.AlterModelOptions(
            name='orderline',
            options={'verbose_name': 'Pozycja na zamówieniu', 'verbose_name_plural': 'Pozycje na zamówieniu'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'verbose_name': 'Produkt', 'verbose_name_plural': 'Produkty'},
        ),
        migrations.AlterModelOptions(
            name='szikpoint',
            options={'verbose_name': 'Punkt SZiK', 'verbose_name_plural': 'Punkty SZiK'},
        ),
        migrations.AlterModelOptions(
            name='usertype',
            options={'verbose_name': 'Typ użytkownika', 'verbose_name_plural': 'Typy użytkowników'},
        ),
        migrations.AlterModelOptions(
            name='vinnumber',
            options={'verbose_name': 'Numer VIN', 'verbose_name_plural': 'Numery VIN'},
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='city',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='postal_code',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='street_address',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='telephone',
            field=models.CharField(max_length=9, null=True),
        ),
    ]