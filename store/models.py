from django.db import models
import uuid

# Create your models here.


class Product(models.Model):
    PRODUCT_TYPES = (
        ("Pizza", "pizza"),
        ("Nonpizza", "nonpizza")
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField(blank=True, null=True)
    desc = models.TextField(max_length=500)
    image = models.ImageField(blank=True, upload_to='images')
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    product_type = models.CharField(max_length=10, choices=PRODUCT_TYPES)

    def __str__(self):
        return self.name

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

    @property
    def check_variant(self):
        # reverse accessor
        print(self.productvariant_set.size())
        return True


class Size(models.Model):
    name = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    price = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.title} - price: ${self.price}"
