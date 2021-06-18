from django import template
from ..models import Order

register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(customer=user, ordered=False)
        if qs.exists():
            return qs[0].order_lines.count()
    return 0
