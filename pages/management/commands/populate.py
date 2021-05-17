from django.core.management.base import BaseCommand, CommandError

from model_bakery import baker


class Command(BaseCommand):
    help = 'Populates the database with random data'

    def handle(self, *args, **options):
        baker.make('pages.Product', _quantity=1000)
        baker.make('pages.Category', _quantity=20)
        baker.make('pages.SzikPoint', _quantity=50)
