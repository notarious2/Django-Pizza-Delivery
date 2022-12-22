from django.db import models
from users.models import Customer
import uuid
from store.models import Product, ProductVariant
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.


class Order(models.Model):
    transaction_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=True)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE)

    date_ordered = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    complete = models.BooleanField(default=False)

    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.transaction_id} by {self.customer}"

    @property
    def get_cart_subtotal(self):
        order_items = self.orderitem_set.all()
        total = sum([item.get_total for item in order_items])
        return total
    # display property name as 'Subtotal' in the admin panel's list display
    get_cart_subtotal.fget.short_description = 'Subtotal'

    @property
    def get_cart_total(self):
        total = self.get_cart_subtotal
        if self.coupon:
            total = total - self.get_coupon_value
        return total
    # display property name as 'Total' in the admin panel's list display
    get_cart_total.fget.short_description = 'Total'

    @property
    def get_cart_items(self):
        order_items = self.orderitem_set.all()
        total = sum([item.quantity for item in order_items])
        return total
    # display property name as '# Items' in the admin panel's list display
    get_cart_items.fget.short_description = '# Items'

    @property
    def get_coupon_value(self):
        # calculate dollar value of the coupon
        # if discount type Percent
        if self.coupon:
            if self.coupon.discount_type == "Percent":
                coupon_value = self.get_cart_subtotal*self.coupon.discount_amount//100
            else:
                coupon_value = self.coupon.discount_amount
        # if discount type Absolute
        else:
            coupon_value = None
        return coupon_value
    # display property name as 'Coupon' in the admin panel's list display
    get_coupon_value.fget.short_description = 'Coupon'


class OrderItem(models.Model):
    """
    There is a one-to-many relationship between OrderItem and Order,
    - one order may have many order items, for this 'order' is added 
    as a foreign key in the OrderItem model. Similary, one OrderItem may contain
    multiple products.
    """
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, null=True, blank=True)
    variation = models.ForeignKey(
        ProductVariant, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    # no string representation added is it is managed in the admin.py

    # get item price for product with and without variation
    @property
    def get_item_price(self):
        if self.product.has_variants:
            return self.variation.price
        else:
            return self.product.price

    # Calculates total based on the quantity of items per individual product
    @property
    def get_total(self):
        if self.product.has_variants:
            total = self.variation.price * self.quantity
        else:
            total = self.product.price * self.quantity
        return total
    # display property name as 'Total' in the admin panel's list display
    get_total.fget.short_description = 'Total'


class Coupon(models.Model):
    DISCOUNT_CHOICES = (
        ("Absolute", "Absolute"),
        ("Percent", "Percent")
    )
    code = models.CharField(max_length=50, unique=True)
    active = models.BooleanField(default=False)
    discount_type = models.CharField(
        max_length=10, choices=DISCOUNT_CHOICES, default="Percent")
    discount_amount = models.PositiveIntegerField(null=True, blank=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    stripe_api_id = models.CharField(max_length=200, null=True, blank=True)
    stripe_coupon_id = models.CharField(
        max_length=50, null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.code} type: {self.discount_type} value: {self.discount_amount}"


class ShippingAddress(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    address_1 = models.CharField(max_length=50)
    address_2 = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=30)
    country = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=6, blank=True, null=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return f"{self.customer} {self.first_name} {self.last_name} {self.address_1}"
