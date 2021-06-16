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
from .models import BillingAddress, Item, Order, OrderItem, Payment, Coupon

# This is a sample test API key. Sign in to see examples pre-filled with your key.
stripe.api_key = settings.STRIPE_SECRET_KEY


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
    paginate_by = 12


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


class CheckoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            coupon_form = CouponForm()
            form = CheckoutForm()
            context = {
                'order': order,
                'form': form,
                'coupon_form': coupon_form,
                'DISPLAY_COUPON_FORM': True
            }
            return render(request, 'shop/checkout.html', context)
        except ObjectDoesNotExist:
            messages.error(
                request, 'You do not have an order yet, keep shopping.')
            return redirect('store:home')

    def post(self, request, *args, **kwargs):
        form = CheckoutForm(request.POST or None)
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            if form.is_valid():
                user = request.user
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip_code = form.cleaned_data.get('zip_code')
                billing_adress = BillingAddress(
                    user=user, street_address=street_address, apartment_address=apartment_address, country=country, zip_code=zip_code)
                order.billing_address = billing_adress
                billing_adress.save()
                order.save()
                payment_option = form.cleaned_data.get('payment_option')
                if payment_option == 'S':
                    return redirect('store:payment', payment_option='stripe')
                else:
                    return redirect('store:payment', payment_option='paypal')
            else:
                messages.error(
                    request, 'Your information is invalid, please check again.')
        except ObjectDoesNotExist:
            messages.error(request, 'You do not have an order')
            return redirect('store:home')
        return redirect('store:checkout')


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
        return redirect("core:checkout")


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
