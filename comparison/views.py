
from django.apps import apps
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST
from django.http.response import JsonResponse
from django.template.loader import render_to_string

from comparison.config import COMPARISON_CATEGORY_MODEL
from collections import defaultdict


def prepare_attributes(products):
    all_attributes = set()
    for product in products:
        if product.attributes:
            for key, value in dict(product.attributes).items():
                all_attributes.add(key)
                print('size of all:', len(all_attributes))

    attribute_map = defaultdict(list)
    for attribute in all_attributes:
        for count, product in enumerate(products):
            if product.attributes and attribute in product.attributes:
                print('size of prodict attrs:', len(product.attributes))
                attribute_map[attribute].append(str(product.attributes[attribute]))
            else:
                attribute_map[attribute].append('-')
    return dict(attribute_map)


def index(request, category_id):
    category_model = apps.get_model(COMPARISON_CATEGORY_MODEL)

    category = get_object_or_404(category_model, id=category_id)

    products = request.comparison.get_products(category_id)

    context = {
        'category': category,
        'products': products,
        'attributes': prepare_attributes(products)
    }

    return render(request, 'comparison/index.html', context)


@require_POST
@csrf_exempt
def toggle(request, product_id):

    if request.comparison.has_product(product_id):
        return remove(request, product_id)

    return add(request, product_id)


@require_POST
@csrf_exempt
def add(request, product_id):
    return _action_view(
        request,
        product_id,
        action=lambda p: request.comparison.add(p),
        message=lambda p: _('{} added to comparison').format(p.name))


@require_POST
@csrf_exempt
def remove(request, product_id):
    return _action_view(
        request,
        product_id,
        action=lambda p: request.comparison.remove(p),
        message=lambda p: _('{} removed from comparison').format(p.name))


def _action_view(request, product_id, action, message):

    product = get_object_or_404(
        apps.get_model('pages', 'Product'), id=product_id)

    action(product)

    print(message(product)) # TODO: REMOVE

    if not request.is_ajax():
        return redirect(request.POST.get('next', 'home'))

    return JsonResponse({
        'message': message(product),
        'dropdown': render_to_string(
            'comparison/dropdown.html', request=request),
        'is_active': request.comparison.has_product(product_id)
    })
