from django.contrib import admin
from .models import Order, OrderItem, Coupon, ShippingAddress, PickUpDetail


class OrderItemInline(admin.TabularInline):
    model = OrderItem

class OrderInline(admin.TabularInline):
    model = Order
    # specify fields visible in inline Order field
    # readonly_fields = ('transaction_id',)

class ShippingInline(admin.TabularInline):
    model = ShippingAddress
    # # remove permission to modify
    # def has_change_permission(self, request, obj):
    #     return False
    # # remove permission to add
    # def has_add_permission(self, request, obj):
    #     return False

class PickUpDetailInline(admin.TabularInline):
    model = PickUpDetail

        
class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'transaction_id', 'complete', 'paid', 'delivery_method', 'date_ordered',
                    'date_modified', 'get_cart_items', 'get_cart_subtotal',
                    'get_coupon_value', 'get_cart_total')
    # list_filter = ('complete',)
    search_fields = ['transaction_id']
    # new in Django 4
    search_help_text = 'search by transaction id'
    ordering = ("-complete", '-date_modified')
    # list_editable = ('complete',)
    # readonly_fields = ('customer', 'transaction_id',
    #                    'date_ordered', 'date_modified', 'delivery_method', 'payment_method', 'paid')
    # make all fields read-only
    def has_change_permission(self, request, obj=None):
        return False
    inlines = []
    
    # display inlines based on condition
    def get_inlines(self, request, obj):
        if obj.delivery_method == "carryout":
            return [OrderItemInline, PickUpDetailInline]
        elif obj.delivery_method == "delivery":
            return [OrderItemInline, ShippingInline]
        else:
            return [OrderItemInline, ShippingInline, PickUpDetailInline]



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
    
    # displays all fields
    # list_display = [field.name for field in OrderItem._meta.get_fields()]

class PickUpDetailAdmin(admin.ModelAdmin):
    # grab transaction id from order
    @admin.display(description='Transaction ID')
    def transaction_id(self, obj):
        return obj.order.transaction_id
    list_display = ('transaction_id', 'urgency', 'pickup_date', 'phone', 'email')
    readonly_fields = ('order',)

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
    list_display = ('transaction_id', 'order_updated', 'phone', 'email', 'address_1', 'city')
    readonly_fields = ('order',)

admin.site.register(PickUpDetail, PickUpDetailAdmin)
admin.site.register(ShippingAddress, ShippingAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Coupon, CouponAdmin)
