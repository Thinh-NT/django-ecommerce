from django.urls.conf import path
from .views import (
    HomeView, ItemDetailView,
    add_item_to_cart, remove_from_cart, remove_single_item_from_cart,
    add_single_item_to_cart, remove_item_from_cart,
    OrderSummaryView, CheckoutView, PaymentView,
)

app_name = 'store'

urlpatterns = [
    path(route='', view=HomeView.as_view(), name='home'),
    path(route='product/<slug>', view=ItemDetailView.as_view(), name='product'),
    path(route='order-summary/',
         view=OrderSummaryView.as_view(), name='order-summary'),
    path(route='checkout/',
         view=CheckoutView.as_view(), name='checkout'),
    path(route='payment/<payment_option>',
         view=PaymentView.as_view(), name='payment'),
    path(route='add_item_to_cart/<slug>',
         view=add_item_to_cart, name='add-item-to-cart'),
    path(route='remove_from_cart/<slug>',
         view=remove_from_cart, name='remove-from-cart'),
    path(route='remove-single-item-from-cart/<slug>',
         view=remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path(route='add-single-item-to-cart/<slug>',
         view=add_single_item_to_cart, name='add-single-item-to-cart'),
    path(route='remove-item-from-cart/<slug>',
         view=remove_item_from_cart, name='remove-item-from-cart')
]
