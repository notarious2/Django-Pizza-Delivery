from django.contrib import admin
from .models import Order, OrderItem

# Register your models here.

# to display specific fields of the model


class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'complete', 'date_ordered',
                    'date_modified', 'transaction_id')


class OrderItemAdmin(admin.ModelAdmin):
    list_display = [field.name for field in OrderItem._meta.get_fields()]


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
