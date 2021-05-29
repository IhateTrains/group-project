# pages/views.py

# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import ListView, DetailView, View
# project
from .models import Product, Category, Order, OrderLine, SzikPoint
from .forms import CreateUserForm, CreateProfileForm
from . import services


class HomeView(ListView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_list'] = Product.objects.all()  # temporary
        context['categories'] = Category.objects.all()  # temporary
        return context

    def get_queryset(self):
        return Product.objects.all()


class SalesView(ListView):
    model = Product
    template_name = "pages/sales.html"


class ProductView(DetailView):
    model = Product
    template_name = "pages/product.html"


class ShopsView(ListView):
    model = SzikPoint
    template_name = "pages/shops.html"


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(customer=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'pages/order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an order")
            return redirect("/")


def about(request):
    return HttpResponse('Projekt grupowy z Inżynierii Oprogramowania.')


def get_nearest_shop(request, lat, lng):
    nearest_shop_data = services.get_nearest_shop_data(lat, lng)
    return JsonResponse(nearest_shop_data)


def search_products(request):
    if request.method == 'POST':
        searched = request.POST['searched']
        matching_products = services.get_matching_products(searched)
        return render(request, 'pages/search_products.html',
                      {'searched': searched,
                       'matching_products': matching_products})
    return render(request, 'pages/search_products.html', {})


def get_category_product_list(request, pk):
    context = {
        'products': Product.objects.filter(category_id=pk),
        'hide_category_on_product_cards': 'True'
    }
    return render(request, 'pages/category.html', context=context)


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
            return redirect("pages:order-summary")
        else:
            order.products.add(order_item)
            messages.info(request, "Dodano do koszyka")
            return redirect("pages:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(customer=request.user, order_date=ordered_date)
        order.products.add(order_item)
        messages.info(request, "Dodano do koszyka")
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
            messages.info(request, "Usunięto \"" + order_item.product.name + "\" z koszyka")
            return redirect("pages:order-summary")
        else:
            messages.info(request, "Produktu nie ma w koszyku")
            return redirect("pages:product", pk=pk)
    else:
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
            return redirect("pages:order-summary")
        else:
            messages.info(request, "Produktu nie ma w koszyku")
            return redirect("pages:order-summary")
    else:
        return redirect("pages:order-summary")


def registerView(request):
    form = CreateUserForm()
    form_prof = CreateProfileForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        form_prof = CreateProfileForm(request.POST)
        if form.is_valid() and form_prof.is_valid():
            user = form.save()
            user.refresh_from_db()
            form_prof = CreateProfileForm(request.POST, instance=user.userprofile)
            form_prof.full_clean()
            form_prof.save()
            user.save()
            return redirect('/')
    context = {'form': form, 'form_prof': form_prof}
    return render(request, 'register.html', context)

def contact(request):
    szik_points = SzikPoint.objects.all()
    return render(request, 'pages/contact.html', {'szik_points': szik_points})

def search_points(request):
    if request.method == 'POST':
        searched = request.POST['searched']
        if searched != '':
            szik_points = SzikPoint.objects.filter(city=searched)
            return render(request, 'pages/search_points.html',
                      {'searched': searched,
                       'szik_points': szik_points})
        else:
            szik_points = SzikPoint.objects.all()
            return render(request, 'pages/search_points.html', {'szik_points': szik_points})

def users_orders_list(request):
    user = request.user
    list = Order.objects.filter(customer=user)
    orders_list = list.order_by('-order_date')

    return render(request, 'pages/orders_list.html', {'orders_list': orders_list})

