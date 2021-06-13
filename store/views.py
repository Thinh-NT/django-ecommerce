from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Item, Order, OrderItem
from django.views.generic import ListView, DetailView
from django.utils import timezone


class HomeView(ListView):
    model = Item
    context_object_name = 'items'
    template_name = 'shop/home.html'
    paginate_by = 12


class ItemDetailView(DetailView):
    model = Item
    template_name = 'shop/product.html'
    context_object_name = 'item'


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
