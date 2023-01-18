from django.db import models
from django.utils.safestring import mark_safe
import uuid

# Create your models here.


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    price = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True)
    desc = models.TextField(max_length=500, blank=True, null=True)
    image = models.ImageField(blank=True, upload_to='images')
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    product_category = models.ForeignKey(
        "Category", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        """Order by product category"""
        ordering = ('product_category',)

    def __str__(self):
        return self.name

    # to display image in the admin panel
    def image_tag(self):
        if self.image:
            return mark_safe(f'<img src="{self.image.url}" width="100" height="100" />')
    image_tag.short_description = 'Image'

    @property
    def get_product_variants(self):
        # reverse accessor
        variants = self.productvariant_set.all()
        return variants

    @property
    def has_variants(self):
        if self.productvariant_set.count() > 0:
            return True
        else:
            return False


class Category(models.Model):
    name = models.CharField(max_length=20, unique=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=20, blank=True, null=True, unique=True)

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.title} - price: ${self.price}"

    @property
    def get_size(self):
        # return size as a string
        return str(self.size)
