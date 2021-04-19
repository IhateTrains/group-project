# pages/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import ListView, DetailView, View
from .models import Product, Order, OrderLine


class HomeView(ListView):
    model = Product
    template_name = "pages/home.html"


class ProductView(DetailView):
    model = Product
    template_name = "pages/product.html"


def about(request):
    return HttpResponse('Projekt grupowy z Inżynierii Oprogramowania.')


@login_required
def add_to_cart(request, pk):
    item = get_object_or_404(Product, pk=pk)
    order_item, created = OrderLine.objects.get_or_create(
        product=item,
        customer=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(customer=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]

        if order.products.filter(product__pk=item.pk).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Added quantity to Product")
            return redirect("pages:order-summary")
        else:
            order.products.add(order_item)
            messages.info(request, "Product added to your cart")
            return redirect("pages:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(customer=request.user, orderDate=ordered_date)
        order.products.add(order_item)
        messages.info(request, "Product added to your cart")
        return redirect("pages:order-summary")


@login_required
def remove_from_cart(request, pk):
    item = get_object_or_404(Product, pk=pk)
    order_qs = Order.objects.filter(
        customer=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.products.filter(product__pk=item.pk).exists():
            order_item = OrderLine.objects.filter(
                product=item,
                customer=request.user,
                ordered=False
            )[0]
            order_item.delete()
            messages.info(request, "Item \"" + order_item.product.product_name + "\" remove from your cart")
            return redirect("pages:order-summary")
        else:
            messages.info(request, "This Item not in your cart")
            return redirect("pages:product", pk=pk)
    else:
        messages.info(request, "You do not have an Order")
        return redirect("pages:product", pk=pk)


@login_required
def reduce_quantity_item(request, pk):
    item = get_object_or_404(Product, pk=pk)
    order_qs = Order.objects.filter(customer=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.products.filter(product__pk=item.pk).exists():
            order_item = OrderLine.objects.filter(product=item, customer=request.user, ordered=False)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order_item.delete()
            messages.info(request, "Product quantity was updated")
            return redirect("pages:order-summary")
        else:
            messages.info(request, "This Product not in your cart")
            return redirect("pages:order-summary")
    else:
        messages.info(request, "You do not have an Order")
        return redirect("pages:order-summary")
