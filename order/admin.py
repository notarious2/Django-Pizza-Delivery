from django.contrib import admin
from .models import Order, OrderItem, Coupon, ShippingAddress, PickUpDetail


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('image_tag',)


class OrderInline(admin.TabularInline):
    model = Order

    # remove permission to modify
    def has_change_permission(self, request, obj):
        return False
    # remove permission to add

    def has_add_permission(self, request, obj):
        return False


class ShippingInline(admin.TabularInline):
    model = ShippingAddress


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

    # def has_change_permission(self, request, obj=None):
    #     return False
    inlines = [OrderItemInline]


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'get_variation', 'get_total',
                    'date_added')
    readonly_fields = ('image_tag',)

    # display attribute of foreign key field in the admin panel
    @admin.display(description='Title')
    def get_variation(self, obj):
        if obj.variation:
            # display name of variation
            return obj.variation.title
        else:
            # display name of the product
            return obj.product.name


class CouponAdmin(admin.ModelAdmin):
    inlines = [OrderInline]


class PickUpDetailAdmin(admin.ModelAdmin):
    list_display = ('urgency',
                    'pickup_date')
    inlines = [OrderInline]


class ShippingAdmin(admin.ModelAdmin):
    inlines = [OrderInline]
    list_display = ('address_1', 'first_name', 'last_name')


admin.site.register(PickUpDetail, PickUpDetailAdmin)
admin.site.register(ShippingAddress, ShippingAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Coupon, CouponAdmin)
