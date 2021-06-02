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
        fields = ['category', 'name', 'price', 'discount']

    @staticmethod
    def products_filter(queryset, name, value):
        expr = 'name'  # fallback
        if value == 'name_ascending':
            expr = 'name'
        elif value == 'name_descending':
            expr = '-name'
        elif value == 'price_ascending':
            return queryset.extra(select={'price_val': 'CASE WHEN discount IS NULL THEN price '
                                                       'ELSE price-discount END'},
                                  order_by=['price_val'])
        elif value == 'price_descending':
            return queryset.extra(select={'price_val': 'CASE WHEN discount IS NULL THEN price '
                                                       'ELSE price-discount END'},
                                  order_by=['-price_val'])
        return queryset.order_by(expr)
