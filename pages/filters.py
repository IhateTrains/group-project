import django_filters

from .models import Product

class ProductFilter(django_filters.FilterSet):

    CHOICES = (
        ('ascending', 'Ceny rosnąco'),
        ('descending', 'Ceny malejąco')
    )

    pricing = django_filters.ChoiceFilter(label='Pricing', choices=CHOICES, method='filter_by_price')

    class Meta:
        model = Product
        fields = ['category', 'name', 'price']
    
    def filter_by_price(self, queryset, name, value):
        
        expr = 'price' if value == 'ascending' else '-price'
        return queryset.order_by(expr)
        