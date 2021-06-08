from django.db.models import Q
from .models import SzikPoint, Product, Category
from .serializers import SzikPointSerializer
from django.core.paginator import Paginator
from .filters import ProductFilter


def get_nearest_shop_data(lat, lng):
    """
        Haversine Formula
        https://en.wikipedia.org/wiki/Haversine_formula
        doesn't require GeoDjango :)
    """

    latitude_col = '"map_latitude"'
    longitude_col = '"map_longitude"'

    query = """SELECT id, (6367*acos(cos(radians( %2f ))
                               *cos(radians( %s ))*cos(radians( %s )-radians( %2f ))
                               +sin(radians( %2f ))*sin(radians( %s ))))
                               AS distance FROM pages_szikpoint ORDER BY distance LIMIT 1""" % (
        float(lat),
        latitude_col,
        longitude_col,
        float(lng),
        float(lat),
        latitude_col
    )

    query_set = SzikPoint.objects.raw(query)[0]
    serializer = SzikPointSerializer(query_set)
    return serializer.data


def get_matching_products(searched):
    return Product.objects.filter(Q(name__icontains=searched)
                                  | Q(description__icontains=searched))

def get_products_and_categories(request, on_sale=False):
    context = { 'section': None }
    selected_category_pk = request.GET.get('category')
    if selected_category_pk is not None and len(selected_category_pk) > 0:
        
        selected_category = Category.objects.get(pk=selected_category_pk)

        if selected_category.parent_category is not None:
            section_pk = selected_category.parent_category.pk
            product_list = Product.objects.filter(category=selected_category_pk)
        else:
            section_pk = selected_category.pk
            product_list = Product.objects.filter(category__parent_category=section_pk)
            product_list |= Product.objects.filter(category=section_pk)

        context['categories'] = Category.objects.filter(parent_category=section_pk)
    else:
        section_pk = None
        context['categories'] = Category.objects.filter(parent_category__isnull=True)
        product_list = Product.objects.all()

    if section_pk is not None:
        context['section'] = Category.objects.get(pk=section_pk)

    if on_sale:
        product_list = product_list.filter(discount__isnull=False)
    
    context['product_list'] = product_list
    return context

def get_product_list_page(request, product_list):

    product_list = product_list.order_by('category__parent_category', 'category')
    product_filter = ProductFilter(request.GET, queryset=product_list)
    paginator = Paginator(product_filter.qs, 12)
    page_number = request.GET.get('page')

    if page_number is None or len(page_number) == 0:
        page_number = 1

    return paginator.get_page(page_number)
    