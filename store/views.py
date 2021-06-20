import json

from django.http.response import HttpResponseRedirect, JsonResponse

import stripe
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import DetailView, ListView, View

from .forms import CheckoutForm, CouponForm
from .models import Address, Item, Order, OrderItem, Payment, Coupon

# This is a sample test API key. Sign in to see examples pre-filled with your key.
stripe.api_key = settings.STRIPE_SECRET_KEY


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class CreatePayment(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            intent = stripe.PaymentIntent.create(
                amount=int(order.total()*100),
                currency='usd',
                payment_method_types=["card"]
            )
            payment = Payment()
            payment.code = intent['id']
            payment.user = request.user
            payment.amount = order.total()
            order.payment = payment
            order.ordered = True
            payment.save()
            order.save()

            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()
            return JsonResponse({
                'clientSecret': intent['client_secret']
            })
        except stripe.error.CardError as e:
            messages.warning(request, "Please check your card's information.")
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(request, "Traffic, please try again.")
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.warning(request, "Invalid request, please try again")
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.warning(
                request, "You can make transaction now, please try again later.")
        except stripe.error.APIConnectionError as e:
            messages.warning(request, "Please check your network again.")
        except stripe.error.StripeError as e:
            messages.warning(
                request, "Something wrong with me, I have received an email about it, sorry.")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class HomeView(ListView):
    model = Item
    context_object_name = 'items'
    template_name = 'shop/home.html'
    # paginate_by = 12


class ItemDetailView(DetailView):
    model = Item
    template_name = 'shop/product.html'
    context_object_name = 'item'


class PaymentView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            context = {
                'order': order,
            }
            return render(request, 'shop/payment.html', context)
        except ObjectDoesNotExist:
            messages.error(
                request, 'You do not have an order yet, keep shopping.')
            return redirect('store:home')

class CheckoutView(View):
    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }

            shipping_address_qs = Address.objects.filter(
                user=request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})

            billing_address_qs = Address.objects.filter(
                user=request.user,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                context.update(
                    {'default_billing_address': billing_address_qs[0]})
            return render(request, "shop/checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(request, "You do not have an active order")
            return redirect("store:checkout")

    def post(self, request, *args, **kwargs):
        form = CheckoutForm(request.POST or None)
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            if form.is_valid():
                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print("Using the defualt shipping address")
                    address_qs = Address.objects.filter(
                        user=request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            request, "No default shipping address available")
                else:
                    print("User is entering a new shipping address")
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([shipping_address1, shipping_country, shipping_zip]):
                        shipping_address = Address(
                            user=request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            zip=shipping_zip,
                            address_type='S'
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(
                            request, "Please fill in the required shipping address fields")

                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                elif use_default_billing:
                    print("Using the defualt billing address")
                    address_qs = Address.objects.filter(
                        user=request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            request, "No default billing address available")
                        return redirect('store:checkout')
                else:
                    print("User is entering a new billing address")
                    billing_address1 = form.cleaned_data.get(
                        'billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    billing_country = form.cleaned_data.get(
                        'billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')

                    if is_valid_form([billing_address1, billing_country, billing_zip]):
                        billing_address = Address(
                            user=request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            zip=billing_zip,
                            address_type='B'
                        )
                        billing_address.save()

                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get(
                            'set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()

                    else:
                        messages.info(
                            request, "Please fill in the required billing address fields")
                        return redirect('store:checkout')

                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 'S':
                    return redirect('store:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('store:payment', payment_option='paypal')
                else:
                    messages.warning(
                        request, "Invalid payment option selected")
                    return redirect('store:checkout')
        except ObjectDoesNotExist:
            messages.warning(request, "You do not have an active order")
            return redirect("store:order-summary")
class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            context = {'order': order}
        except ObjectDoesNotExist:
            messages.error(
                request, 'You do not have an order yet, keep shopping.')
            return redirect('store:home')
        return render(request, 'shop/order_summary.html', context)


@ login_required
def add_item_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, _ = OrderItem.objects.get_or_create(
        item=item, user=request.user, ordered=False
    )
    print(_)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, 'Item quantity was updated')
        else:
            order.items.add(order_item)
            messages.info(request, 'Item bas been added to your cart')
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date
        )
        order.items.add(order_item)
        messages.info(request, 'Item bas been added to your cart')

    return redirect('store:product', slug=slug)


@ login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item, user=request.user, ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, 'Item has been remove from your cart')
        else:
            messages.info(request, 'This item is not in your cart')
    else:
        messages.info(request, 'You do not have an order yet')
    return redirect('store:product', slug=slug)


@ login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item, user=request.user, ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                messages.info(request, 'Item quantity has been updated')
            else:
                order.items.remove(order_item)
                messages.info(request, 'Item has been remove from your cart')
    return redirect('store:order-summary')


@ login_required
def add_single_item_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, _ = OrderItem.objects.get_or_create(
        item=item, user=request.user, ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    order = order_qs[0]
    if order.items.filter(item__slug=item.slug).exists():
        order_item.quantity += 1
        order_item.save()
        messages.info(request, 'Item quantity was updated')
    return redirect('store:order-summary')


@ login_required
def remove_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    order = order_qs[0]
    if order.items.filter(item__slug=item.slug).exists():
        order_item = OrderItem.objects.filter(
            item=item, user=request.user, ordered=False
        )[0]
        order.items.remove(order_item)
        messages.info(request, 'Item has been remove from your cart')
    return redirect('store:order-summary')


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("store:checkout")


def add_coupon_view(request):
    form = CouponForm(request.POST or None)
    if form.is_valid():
        try:
            code = form.cleaned_data.get('code')
            order = Order.objects.get(
                user=request.user, ordered=False)
            order.coupon = get_coupon(request, code)
            order.save()
            messages.success(request, "Successfully added coupon")
            return redirect("store:checkout")
        except ObjectDoesNotExist:
            messages.info(request, "You do not have an active order")
            return redirect("store:checkout")
