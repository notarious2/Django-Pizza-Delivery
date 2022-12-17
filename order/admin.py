from django.contrib import admin
from .models import Order, OrderItem, Coupon

# Register your models here.

# to display specific fields of the model


class OrderItemInline(admin.TabularInline):
    model = OrderItem

# add order inline to the coupon


class OrderInline(admin.TabularInline):
    model = Order
    # specify fields visible in inline Order field
    readonly_fields = ('transaction_id',)


class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'complete', 'date_ordered',
                    'date_modified', 'get_cart_items', 'get_cart_subtotal',
                    'get_coupon_value', 'get_cart_total')
    inlines = [OrderItemInline]


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'get_variation', 'get_total',
                    'date_added')

    # display attribute of foreign key field in the admin panel
    @admin.display(description='Title')
    def get_variation(self, obj):
        if obj.variation:
            # display name of variation
            return obj.variation.title
        else:
            # display name of the product
            return obj.product.name

    # list_display = [field.name for field in OrderItem._meta.get_fields()]


class CouponAdmin(admin.ModelAdmin):
    inlines = [OrderInline]


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Coupon, CouponAdmin)
