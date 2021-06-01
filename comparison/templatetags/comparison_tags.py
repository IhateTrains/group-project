
from django import template

register = template.Library()


@register.filter
def is_compared(object_id, request):
    return request.comparison.has_product(object_id)
