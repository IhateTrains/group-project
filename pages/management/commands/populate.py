from django.core.management.base import BaseCommand

from model_bakery import baker
from ... import models


class Command(BaseCommand):
    help = 'Populates the database with random data'

    def handle(self, *args, **options):
        if models.Product.objects.count() < 2000:
            for cat_name in ('Silniki', 'Zderzaki', 'Reflektory', 'Płyny'):
                new_category = baker.make('pages.Category', name=cat_name)
                baker.make('pages.Product', category_id=new_category.pk, _quantity=150)
            self.stdout.write(self.style.SUCCESS('Successfully populated Products'))
        if models.SzikPoint.objects.count() < 50:
            baker.make('pages.SzikPoint', _quantity=50, _create_files=True)
            self.stdout.write(self.style.SUCCESS('Successfully populated SzikPoints'))
