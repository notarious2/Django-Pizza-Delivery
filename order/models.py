from django.db import models
from users.models import Customer
import uuid
from store.models import Product, ProductVariant
import datetime
from django.utils.safestring import mark_safe
from django.utils import timezone


# Create your models here.


class Order(models.Model):
    PAYMENT_CHOICES = (("cash", "cash"), ("online", "online"))
    DELIVERY_CHOICES = (("delivery", "delivery"), ("carryout", "carryout"))
    transaction_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=True
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    date_ordered = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    complete = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    delivery_method = models.CharField(max_length=10, choices=DELIVERY_CHOICES)
    shipping = models.ForeignKey(
        "ShippingAddress", on_delete=models.SET_NULL, blank=True, null=True
    )
    pickup = models.ForeignKey(
        "PickUpDetail", on_delete=models.SET_NULL, blank=True, null=True
    )
    coupon = models.ForeignKey(
        "Coupon", on_delete=models.SET_NULL, blank=True, null=True
    )
    email = models.EmailField(max_length=70, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.transaction_id} by {self.customer}"

    @property
    def get_cart_subtotal(self):
        order_items = self.orderitem_set.all()
        total = sum([item.get_total for item in order_items])
        return total

    # display property name as 'Subtotal' in the admin panel's list display
    get_cart_subtotal.fget.short_description = "Subtotal"

    @property
    def get_cart_total(self):
        total = self.get_cart_subtotal
        if self.coupon:
            total = total - self.get_coupon_value
        return total

    # display property name as 'Total' in the admin panel's list display
    get_cart_total.fget.short_description = "Total"

    @property
    def get_cart_items(self):
        order_items = self.orderitem_set.all()
        total = sum([item.quantity for item in order_items])
        return total

    # display property name as '# Items' in the admin panel's list display
    get_cart_items.fget.short_description = "# Items"

    # show product titles in the order
    @property
    def display_items(self):
        """To nicely display order items in Orders tab of a registered user"""
        order_items = self.orderitem_set.all()
        ticker, l = 1, len(order_items)
        product_titles = str()
        for item in order_items:
            add_comma = ", " if l > 1 and ticker != l else ""
            if item.variation:
                product_title = f"""{item.product.name}
                ({item.variation.get_size},
                #{item.quantity}, ${item.get_total}){add_comma}"""
            else:
                product_title = f"""{item.product.name}
                (#{item.quantity}, ${item.get_total}){add_comma}"""
            product_titles += product_title
            ticker += 1
        return product_titles

    @property
    def get_coupon_value(self):
        # calculate dollar value of the coupon
        # if discount type Percent
        if self.coupon:
            if self.coupon.discount_type == "Percent":
                coupon_value = round(
                    self.get_cart_subtotal * self.coupon.discount_amount / 100, 2
                )
            else:
                coupon_value = self.coupon.discount_amount
        # if discount type Absolute
        else:
            coupon_value = None
        return coupon_value

    # display property name as 'Coupon' in the admin panel's list display
    get_coupon_value.fget.short_description = "Coupon"


class OrderItem(models.Model):
    """
    There is a one-to-many relationship between OrderItem and Order,
    - one order may have many order items, for this 'order' is added
    as a foreign key in the OrderItem model. Similary, one OrderItem may contain
    multiple products.
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    variation = models.ForeignKey(
        ProductVariant, on_delete=models.SET_NULL, blank=True, null=True
    )
    quantity = models.IntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} #{self.quantity}"

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
    get_total.fget.short_description = "Total"

    # to display image in the admin panel
    def image_tag(self):
        return mark_safe(
            f'<img src="{self.product.image.url}" width="100" height="100" />'
        )

    image_tag.short_description = "Image"


class Coupon(models.Model):
    DISCOUNT_CHOICES = (("Absolute", "Absolute"), ("Percent", "Percent"))
    code = models.CharField(max_length=50, unique=True)
    active = models.BooleanField(default=False)
    discount_type = models.CharField(
        max_length=10, choices=DISCOUNT_CHOICES, default="Percent"
    )
    discount_amount = models.PositiveIntegerField()
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    stripe_coupon_id = models.CharField(
        max_length=50, null=True, blank=True, default=None
    )

    def __str__(self):
        return f"{self.code} type: {self.discount_type} value: {self.discount_amount}"


class ShippingAddress(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    address_1 = models.CharField(max_length=50)
    address_2 = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=30)
    country = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=6, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.address_1}"


class PickUpDetail(models.Model):
    URGENCY_CHOICES = (("asap", "asap"), ("custom", "custom"))
    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES)
    pickup_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.urgency}"
