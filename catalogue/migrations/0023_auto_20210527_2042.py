# Generated by Django 3.1.11 on 2021-05-27 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0022_auto_20210527_1937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productimage',
            name='original',
            field=models.ImageField(blank=True, null=True, upload_to='catalogue.ProductImageStorage/bytes/filename/mimetype'),
        ),
    ]
