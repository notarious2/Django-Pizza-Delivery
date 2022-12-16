from django.contrib import admin
from .models import Product, Size, ProductVariant
# Register your models here.


class ProductVariantsInline(admin.TabularInline):
    model = ProductVariant


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'has_variants', 'image_tag')
    readonly_fields = ['image_tag']
    inlines = [ProductVariantsInline]


admin.site.register(Product, ProductAdmin)
admin.site.register(Size)
admin.site.register(ProductVariant)
