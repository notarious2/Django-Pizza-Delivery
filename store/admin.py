from django.contrib import admin
from .models import Product, Size, ProductVariant
# Register your models here.


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')

admin.site.register(Product, ProductAdmin)
admin.site.register(Size)
admin.site.register(ProductVariant)
