from django.contrib import admin
from .models import Product, Size, ProductVariant
# Register your models here.

admin.site.register(Product)
admin.site.register(Size)
admin.site.register(ProductVariant)
