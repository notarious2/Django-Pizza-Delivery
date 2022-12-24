from django.contrib import admin
from .models import Customer
from order.models import Order, OrderItem


class OrderInline(admin.TabularInline):
    model = Order

    # remove permission to modify
    def has_change_permission(self, request, obj):
        return False
    # remove permission to add

    def has_add_permission(self, request, obj):
        return False


class CustomerAdmin(admin.ModelAdmin):
    inlines = [OrderInline]


admin.site.register(Customer, CustomerAdmin)
