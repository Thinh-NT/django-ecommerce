from django.db import models
from django.shortcuts import reverse
from django.conf import settings

CATEGORY_CHOICES = (
    ('S', 'Shirt'),
    ('SW', 'Sport wear'),
    ('OW', 'Outwear'),
)

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger'),
)


class Item(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(
        choices=CATEGORY_CHOICES, max_length=2, default='S')
    label = models.CharField(choices=LABEL_CHOICES, max_length=1, default='P')
    description = models.TextField(default=f'Description of {title}')

    def get_absolute_url(self):
        return reverse('store:product', kwargs={'slug': self.slug})

    def get_final_price(self):
        if self.discount_price:
            return self.discount_price
        else:
            return self.price

    def get_add_item_to_cart_url(self):
        return reverse('store:add-item-to-cart', kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        return reverse('store:remove-from-cart', kwargs={'slug': self.slug})

    def __str__(self) -> str:
        return self.title


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    item = models.ForeignKey(to=Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.quantity} of {self.item.title}'

    def get_total_price(self):
        if self.item.discount_price:
            return self.item.discount_price * self.quantity
        else:
            return self.item.price * self.quantity


class Order(models.Model):
    items = models.ManyToManyField(OrderItem)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(blank=True, null=True)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email
