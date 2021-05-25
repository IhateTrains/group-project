from django.db.models import Q
from .models import SzikPoint, Product
from .serializers import SzikPointSerializer


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
