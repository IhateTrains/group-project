# pages/views.py

# Django
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import File
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import ListView, DetailView, View
from django.core.paginator import Paginator
from django.db.models import Q
# project
import os
from .models import Product, Order, OrderLine, SzikPoint, CheckoutAddress
from .forms import CreateUserForm, CreateProfileForm, UpdateUserForm, UpdateProfileForm, CheckoutForm, PAYMENT
from . import services
from InvoiceGenerator.pdf import SimpleInvoice
# for email confirmation
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

UserModel = get_user_model()


class SalesView(ListView):
    model = Product
    template_name = "pages/sales.html"


def sales_view(request):
    pc = services.get_products_and_categories(request, on_sale=True)
    context = {
        'page_obj': services.get_product_list_page(request, pc['product_list']),
        'categories': pc['categories'],
        'section': pc['section']
    }
    return render(request, 'pages/sales.html', context)


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
        except ObjectDoesNotExist:
            order = Order(customer=self.request.user, ordered=False, order_date=timezone.now())
            order.save()

        context = {
            'object': order
        }
        return render(self.request, 'pages/order_summary.html', context)


def home_view(request):
    pc = services.get_products_and_categories(request)
    context = {
        'special_offers': Product.objects.filter(discount__isnull=False).order_by('discount')[:10],
        'page_obj': services.get_product_list_page(request, pc['product_list']),
        'categories': pc['categories'],
        'section': pc['section']
    }

    return render(request, 'pages/home.html', context)


class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        order = Order.objects.get(customer=self.request.user, ordered=False)
        context = {
            'form': form,
            'order': order
        }
        return render(self.request, 'pages/checkout.html', context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)

        try:
            order = Order.objects.get(customer=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip_code = form.cleaned_data.get('zip_code')
                payment_option = form.cleaned_data.get('payment_option')

                checkout_address = CheckoutAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip_code=zip_code
                )
                checkout_address.save()
                order.checkout_address = checkout_address
                order.save()

                for payment_tuple in PAYMENT:
                    if payment_option == payment_tuple[0]:
                        order.payment_method = payment_tuple[1]
                        order.ordered = True

                        from InvoiceGenerator.api import Invoice, Item, Client, Provider, Creator
                        os.environ["INVOICE_LANG"] = "pl"

                        client = Client(order.customer.username + '\n'
                                        + str(order.customer.email) + '\n'
                                        + order.customer.userprofile.street_address + '\n'
                                        + order.customer.userprofile.postal_code + ' '
                                        + order.customer.userprofile.city
                                        )
                        provider = Provider('Auto Parts', bank_account='2600420569', bank_code='2010')
                        creator = Creator('Jan Kowalski')
                        invoice = Invoice(client, provider, creator)
                        invoice.number = order.id
                        invoice.currency = 'PLN'
                        invoice.currency_locale = 'pl_PL.UTF-8'
                        for order_line in order.products.all():
                            invoice.add_item(Item(order_line.quantity, order_line.product.get_discount_price(),
                                                  description=order_line.product.name, tax=23))

                        pdf_name = "invoice" + str(order.id) + ".pdf"
                        pdf = SimpleInvoice(invoice)
                        pdf.gen(pdf_name)
                        with open(pdf_name, 'rb') as f:
                            order.invoice_file.save(pdf_name, File(f))
                        if os.path.exists(pdf_name):
                            os.remove(pdf_name)

                        order.save()
                        return redirect('pages:orders_list')

                messages.warning(self.request, "Niepoprawna metoda płatności")
                return redirect('pages:checkout')

        except ObjectDoesNotExist:
            messages.error(self.request, "Nie masz żadnego zamówienia")
            return redirect("pages:order-summary")


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


def loginPage(request):
    context = {}

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('pages:home')
        else:
            context['invalid_login'] = True

    return render(request, 'pages/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('pages:home')


def registerView(request):
    form = CreateUserForm()
    form_prof = CreateProfileForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        form_prof = CreateProfileForm(request.POST)

        mail_exists = request.POST.get('email')
        if User.objects.filter(email=mail_exists).exists():
            messages.error(request, "Konto o podanym emailu już istnieje")
            return redirect('pages:register')

        if form.is_valid() and form_prof.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            user.refresh_from_db()
            form_prof = CreateProfileForm(request.POST, instance=user.userprofile)
            form_prof.full_clean()
            form_prof.save()
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Aktywacja konta.'
            message = render_to_string('email_activation.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            messages.success(request, 'Proszę potwierdzić swój adres e-mail aby ukończyć rejestrację.')
            return redirect('pages:login')
    context = {'form': form, 'form_prof': form_prof}
    return render(request, 'pages/register.html', context)


@login_required
def update_profileView(request):
    u_form = UpdateUserForm(instance=request.user)
    u_form_prof = UpdateProfileForm(instance=request.user.userprofile)
    if request.method == 'POST':
        u_form = UpdateUserForm(request.POST, instance=request.user)
        u_form_prof = UpdateProfileForm(request.POST, instance=request.user.userprofile)

        if u_form.is_valid() and u_form_prof.is_valid():
            u_form.save()
            u_form_prof.save()
            messages.success(request, 'Zmiana danych zakończona pomyślnie!')
            return redirect('pages:update_profile')

    context = {'u_form': u_form, 'u_form_prof': u_form_prof}
    return render(request, 'pages/update_profile.html', context)


def contact(request):
    szik_points = SzikPoint.objects.all()
    return render(request, 'pages/contact.html', {'szik_points': szik_points})


def search_points(request):
    if request.method == 'POST':
        searched = request.POST['searched']
        if searched != '':
            szik_points = SzikPoint.objects.filter(Q(city__icontains=searched) |
                                                   Q(street_address__icontains=searched) |
                                                   Q(postal_code__icontains=searched) |
                                                   Q(telephone__icontains=searched)
                                                   )
            return render(request, 'pages/search_points.html',
                          {'searched': searched,
                           'szik_points': szik_points})
        else:
            szik_points = SzikPoint.objects.all()
            return render(request, 'pages/search_points.html', {'szik_points': szik_points})
    else:
        szik_points = SzikPoint.objects.all()
        return render(request, 'pages/search_points.html', {'szik_points': szik_points})


def users_orders_list(request):
    user = request.user
    filtered_list = Order.objects.filter(customer=user, ordered=True)
    orders_list = filtered_list.order_by('-order_date')

    return render(request, 'pages/orders_list.html', {'orders_list': orders_list})


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Dziękujemy za potwierdzenie mailowe. Teraz możesz się zalogować.')
        return redirect('pages:login')
    else:
        return HttpResponse('Link aktywacyjny jest nieprawidłowy!')
