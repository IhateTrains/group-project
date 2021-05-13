# pages/views.py

# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.forms import UserCreationForm
# project
from .models import Product, Order, OrderLine, SzikPoint
from .forms import CreateUserForm, CreateProfileForm
from .serializers import SzikPointSerializer


class HomeView(ListView):
    model = Product
    template_name = "pages/home.html"


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
    """
        Haversine Formula
        https://en.wikipedia.org/wiki/Haversine_formula
        doesn't require GeoDjango :)
    """

    latitude_col = 'map_latitude'
    longitude_col = 'map_longitude'

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

    if connection.vendor == 'postgresql':
        query = """select id, distance
                    from (
                        select id, ( 6371 * acos( cos( radians( %2f ) ) * cos( radians( "pages_szikpoint.map_latitude" ) ) * cos( radians( "pages_szikpoint.map_longitude" ) - radians( %2f ) ) + sin( radians( %2f ) ) * sin( radians( "pages_szikpoint.map_latitude" ) ) ) ) as distance
                        from pages_szikpoint
                    ) as dt
                    order by distance FETCH FIRST ROW ONLY""" % (
            float(lat),
            float(lng),
            float(lat)
        )

    querySet = SzikPoint.objects.raw(query)[0]
    serializer = SzikPointSerializer(querySet)
    return JsonResponse(serializer.data)


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
        order = Order.objects.create(customer=request.user, orderDate=ordered_date)
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
            return redirect("pages:order-summary")
        else:
            messages.info(request, "Produktu nie ma w koszyku")
            return redirect("pages:order-summary")
    else:
        messages.info(request, "You do not have an Order")
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
