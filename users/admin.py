from django.contrib import admin
from .models import Customer
from order.models import Order, OrderItem


class OrderInline(admin.TabularInline):
    model = Order


class CustomerAdmin(admin.ModelAdmin):
    inlines = [OrderInline]


admin.site.register(Customer, CustomerAdmin)
