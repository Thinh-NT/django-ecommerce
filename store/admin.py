from django.contrib import admin
from .models import Coupon, Item, OrderItem, Order, Address, Payment


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_accepted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


class Display(admin.ModelAdmin):
    list_display = [
        'user',
        'ordered',
        'being_delivered',
        'received',
        'refund_requested',
        'refund_accepted',
        'billing_address',
        'payment',
        'coupon'
    ]
    list_display_links = [
        'user',
        'billing_address',
        'payment',
        'coupon'
    ]
    list_filter = [
        'ordered',
        'being_delivered',
        'received',
        'refund_requested',
        'refund_accepted'
    ]
    search_fields = [
        'user__username',
    ]
    actions = [make_refund_accepted]


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, Display)
admin.site.register(Address)
admin.site.register(Payment)
admin.site.register(Coupon)
