from django.contrib import admin
from .models import Order, OrderItem, Coupon, ShippingAddress

# Register your models here.

# to display specific fields of the model


class OrderItemInline(admin.TabularInline):
    model = OrderItem

# add shipping inline to the order


class OrderInline(admin.TabularInline):
    model = Order
    # specify fields visible in inline Order field
    # readonly_fields = ('transaction_id',)


class ShippingInline(admin.TabularInline):
    model = ShippingAddress

    # remove permission to modify
    def has_change_permission(self, request, obj):
        return False
    # remove permission to add

    def has_add_permission(self, request, obj):
        return False


class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'complete', 'date_ordered',
                    'date_modified', 'get_cart_items', 'get_cart_subtotal',
                    'get_coupon_value', 'get_cart_total')
    list_filter = ('complete',)
    # list_editable = ('complete',)
    readonly_fields = ('customer', 'transaction_id',
                       'date_ordered', 'date_modified')
    inlines = [OrderItemInline, ShippingInline]


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


class ShippingAdmin(admin.ModelAdmin):
    # grab transaction id from order
    @admin.display(description='Transaction ID')
    def transaction_id(self, obj):
        return obj.order.transaction_id
    # grab order modified date from order

    @admin.display(description='Order Updated')
    def order_updated(self, obj):
        return obj.order.date_modified
    list_display = ('transaction_id', 'order_updated', 'phone', 'email')
    readonly_fields = ('order',)


admin.site.register(ShippingAddress, ShippingAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Coupon, CouponAdmin)
