from django.urls.conf import path
from .views import HomeView, ItemDetailView, add_item_to_cart, remove_from_cart

app_name = 'store'

urlpatterns = [
    path(route='', view=HomeView.as_view(), name='home'),
    path(route='product/<slug>', view=ItemDetailView.as_view(), name='product'),
    path(route='add_item_to_cart/<slug>',
         view=add_item_to_cart, name='add-item-to-cart'),
    path(route='remove_from_cart/<slug>',
         view=remove_from_cart, name='remove-from-cart')
]
