from django.db import models
from django.contrib.auth.models import User
import uuid
from store.models import Product

# Create your models here.


class Order(models.Model):
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE)

    date_ordered = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return f"{self.transaction_id} by {self.customer.username}"

    @property
    def get_cart_total(self):
        order_items = self.orderitem_set.all()
        total = sum([item.get_total for item in order_items])
        return total

    @property
    def get_cart_items(self):
        order_items = self.orderitem_set.all()
        total = sum([item.quantity for item in order_items])
        return total


class OrderItem(models.Model):
    """
    There is a one-to-many relationship between OrderItem and Order,
    - one order may have many order items, for this 'order' is added 
    as a foreign key in the OrderItem model. Similary, one OrderItem may contain
    multiple products.
    """
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return f"{self.quantity} of {self.product.name} #transaction: {self.order.transaction_id}"

    # Calculates total based on the quantity of items per individual product
    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total
