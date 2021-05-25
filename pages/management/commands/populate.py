from django.core.management.base import BaseCommand

from model_bakery import baker
from ... import models


class Command(BaseCommand):
    help = 'Populates the database with random data'

    def handle(self, *args, **options):
        if models.Product.objects.count < 1000:
            baker.make('pages.Product', _quantity=1000)
            baker.make('pages.Category', _quantity=20)
        if models.SzikPoint.objects.count < 50:
            baker.make('pages.SzikPoint', _quantity=50)
