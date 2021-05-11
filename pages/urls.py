# pages/urls.py
from django.urls import path, include
from django.views.generic import TemplateView
from . import views
from .views import (
    HomeView,
    SalesView,
    ProductView,
    OrderSummaryView,
    add_to_cart,
    remove_from_cart,
    reduce_quantity_item,
)

app_name = 'pages'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('sales', SalesView.as_view(), name='sales'),
    path('shops', TemplateView.as_view(template_name='pages/shops.html'), name='shops'),
    path('about/', views.about, name='about'),
    path('product/<pk>/', ProductView.as_view(), name='product'),
    path('add-to-cart/<pk>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<pk>/', remove_from_cart, name='remove-from-cart'),
    path('reduce-quantity-item/<pk>/', reduce_quantity_item, name='reduce-quantity-item'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('checkout/', HomeView.as_view(), name='checkout'),  # TODO: add CheckOutView
    path('register/',views.registerView, name='register'),
]
