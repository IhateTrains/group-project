# pages/urls.py
from django.urls import path, include
from . import views
from .views import (
    SalesView,
    ProductView,
    OrderSummaryView,
    CheckoutView,
    ShopsView,
    home_view,
    sales_view,
    search_products,
    get_nearest_shop,
    add_to_cart,
    remove_from_cart,
    reduce_quantity_item,
    activate,
)

app_name = 'pages'

urlpatterns = [
    path('', home_view, name='home'),
    path('home/', home_view, name='home'),
    path('about/', views.about, name='about'),
    # sklepy
    path('shops', ShopsView.as_view(), name='shops'),
    path('get-nearest-shop/<str:lat>/<str:lng>/', get_nearest_shop, name='get-nearest-shop'),
    # produkty
    path('product/<pk>/', ProductView.as_view(), name='product'),
    path('sales', sales_view, name='sales'),
    path('search-products', search_products, name='search-products'),
    # koszyk
    path('add-to-cart/<pk>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<pk>/', remove_from_cart, name='remove-from-cart'),
    path('reduce-quantity-item/<pk>/', reduce_quantity_item, name='reduce-quantity-item'),
    # zamówienia
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    # rejestracja
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.registerView, name='register'),
    path('contact/', views.contact, name='contact'),
    path('search-points', views.search_points, name='search-points'),
    path('orders_list/', views.users_orders_list, name='orders_list'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
]
