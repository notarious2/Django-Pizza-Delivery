from django.db import models
from users.models import Customer
import uuid
from store.models import Product, ProductVariant
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.


class Order(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE)

    date_ordered = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)

    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    
    
    def __str__(self):
        return f"{self.transaction_id} by {self.customer}"

    @property
    def get_cart_subtotal(self):
        order_items = self.orderitem_set.all()
        total = sum([item.get_total for item in order_items])
        return total
    
    @property
    def get_cart_total(self):
        total = self.get_cart_subtotal
        if self.coupon:
            total-= total*self.coupon.discount//100
            # to recalcuate coupon amount
            self.coupon_value = self.get_cart_subtotal*self.coupon.discount//100
        return total

    @property
    def get_cart_items(self):
        order_items = self.orderitem_set.all()
        total = sum([item.quantity for item in order_items])
        return total
    
    @property
    def get_coupon_value(self):
        # dollar value of the coupon
        coupon_value = self.get_cart_subtotal*self.coupon.discount//100
        return coupon_value

class OrderItem(models.Model):
    """
    There is a one-to-many relationship between OrderItem and Order,
    - one order may have many order items, for this 'order' is added 
    as a foreign key in the OrderItem model. Similary, one OrderItem may contain
    multiple products.
    """
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, null=True, blank=True)
    variation = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return f"{self.quantity} of {self.product.name} #transaction: {self.order.transaction_id}"

    # Calculates total based on the quantity of items per individual product
    @property
    def get_total(self):
        total = self.variation.price * self.quantity
        return total

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    active = models.BooleanField(default=False) 
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    def __str__(self):
        return self.code