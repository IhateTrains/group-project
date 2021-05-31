import django_filters
import logging

from .models import Product

class ProductFilter(django_filters.FilterSet):

    CHOICES = (
        ('name_ascending', 'Nazwy rosnąco'),
        ('name_descending', 'Nazwy malejąco'),
        ('price_ascending', 'Ceny rosnąco'),
        ('price_descending', 'Ceny rosnąco')
    )

    sorting = django_filters.ChoiceFilter(choices=CHOICES, method='products_filter')

    class Meta:
        model = Product
        fields = ['category', 'name', 'price']

    def products_filter(self, queryset, name, value):
        if value == 'name_ascending':
            expr = 'name'
        elif value == 'name_descending':
            expr = '-name'
        elif value == 'price_ascending':
            expr = 'price'
        elif value == 'price_descending':
            expr = '-price'

        return queryset.order_by(expr)

        