# pages/views.py

# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import ListView, DetailView, View
from django.core.paginator import Paginator
# project
from .models import Product, Category, Order, OrderLine, SzikPoint, CheckoutAddress
from .forms import CreateUserForm, CreateProfileForm, CheckoutForm, PAYMENT
from . import services
from .filters import ProductFilter
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


def home_view(request): # TODO: change this to products_list view and make new home view

    context = {
        'special_offers': Product.objects.filter(discount__isnull=False)
    }

    selected_category_pk = request.GET.get('category')
    if selected_category_pk is not None and len(selected_category_pk) > 0:
        
        selected_category = Category.objects.get(pk=selected_category_pk)

        if selected_category.parent_category is not None:
            section_pk = selected_category.parent_category.pk
            product_list = Product.objects.filter(category=selected_category_pk)
        else:
            section_pk = selected_category.pk
            product_list = Product.objects.filter(category__parent_category=section_pk)

        context['categories'] = Category.objects.filter(parent_category=section_pk)
    else:
        section_pk = None
        context['categories'] = Category.objects.filter(parent_category__isnull=True)
        product_list = Product.objects.all()

    if section_pk is not None:
        context['section'] = Category.objects.get(pk=section_pk)

    context['filter'] = ProductFilter(request.GET, queryset=product_list)

    products_per_page = 12
    paginator = Paginator(context['filter'].qs, products_per_page)
    page_number = request.GET.get('page')
    if page_number == '' or page_number is None:
        page_number = 1
    context['page_obj'] = paginator.get_page(page_number)

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


def get_category_product_list(request, pk):
    context = {
        'category': Category.objects.get(id=pk),
        'subcategories': Category.objects.filter(parent_category_id=pk),
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
