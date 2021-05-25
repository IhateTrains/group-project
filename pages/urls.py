# pages/urls.py
from django.urls import path, include
from . import views
from .views import (
    HomeView,
    SalesView,
    ProductView,
    OrderSummaryView,
    ShopsView,
    search_products,
    get_nearest_shop,
    get_category_product_list,
    add_to_cart,
    remove_from_cart,
    reduce_quantity_item,
)

app_name = 'pages'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', views.about, name='about'),
    # sklepy
    path('shops', ShopsView.as_view(), name='shops'),
    path('get-nearest-shop/<str:lat>/<str:lng>/', get_nearest_shop, name='get-nearest-shop'),
    # produkty
    path('product/<pk>/', ProductView.as_view(), name='product'),
    path('sales', SalesView.as_view(), name='sales'),
    path('search-products', search_products, name='search-products'),
    # kategorie
    path('category/<pk>/', get_category_product_list, name='category'),
    # koszyk
    path('add-to-cart/<pk>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<pk>/', remove_from_cart, name='remove-from-cart'),
    path('reduce-quantity-item/<pk>/', reduce_quantity_item, name='reduce-quantity-item'),
    # zamówienia
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('checkout/', HomeView.as_view(), name='checkout'),  # TODO: add CheckOutView
    # rejestracja
    path('register/', views.registerView, name='register'),
]
