from django.test import TestCase
from store.models import Product, ProductVariant, Category, Size


class TestStoreModels(TestCase):
    """
    Test creation and properties of a product, 
    product variant, category and size
    """

    def setUp(self):
        self.product_data = {
            'name': 'Test product',
            'price': 10,
        }

    def test_create_size(self):
        """Test creation of size"""
        size = Size.objects.create(name='test size')
        self.assertEqual(str(size), 'test size')

    def test_create_category(self):
        """Test creation of category"""
        category = Category.objects.create(name='test category')
        self.assertEqual(str(category), 'test category')

    def test_create_product_without_variant(self):
        """Test creation of a product without variants"""
        product = Product.objects.create(**self.product_data)
        self.assertEqual(str(product), self.product_data['name'])

    def test_create_product_variant(self):
        """Test creation of a product with variants"""
        product = Product.objects.create(**self.product_data)
        size = Size.objects.create(name='Small')
        product_variant = ProductVariant.objects.create(
            title="Test Variant", product=product, size=size, price=10.2)

        self.assertEqual(str(product_variant), "Test Variant - price: $10.2")
        self.assertEqual(product_variant.product, product)
        self.assertEqual(product_variant.product.name,
                         self.product_data['name'])
        self.assertEqual(product_variant.product.price,
                         self.product_data['price'])

        self.assertEqual(product_variant.size, size)
        self.assertEqual(product_variant.size.name, "Small")

    def test_product_variant_property(self):
        """Test get_size property of product variant model"""
        product = Product.objects.create(**self.product_data)
        size = Size.objects.create(name='Small')
        product_variant = ProductVariant.objects.create(
            title="Test Variant", product=product, size=size, price=10.2)
        self.assertEqual(product_variant.get_size, 'Small')

    def test_product_has_variants_property_TRUE(self):
        """
        Test product has variants property 
        for a product with variants
        """
        product = Product.objects.create(**self.product_data)
        size = Size.objects.create(name='Small')
        product_variant = ProductVariant.objects.create(
            title="Test Variant", product=product, size=size, price=10.2)
        self.assertTrue(product.has_variants)

    def test_product_has_variants_property_FALSE(self):
        """
        Test product has variants property 
        for a product without variants
        """
        product = Product.objects.create(**self.product_data)
        self.assertFalse(product.has_variants)

    def test_product_get_product_variants_property_single(self):
        """
        Test product's get_product_variants property
        for a product with single variant
        """
        product = Product.objects.create(**self.product_data)
        size = Size.objects.create(name='Small')
        product_variant = ProductVariant.objects.create(
            title="Test Variant", product=product, size=size, price=10.2)

        self.assertEqual(product.get_product_variants[0], product_variant)

    def test_product_get_product_variants_property_multiple(self):
        """
        Test product's get_product_variants property
        for a product with multiple variants
        """
        product = Product.objects.create(**self.product_data)
        size_1 = Size.objects.create(name='Small')
        size_2 = Size.objects.create(name='Medium')
        ProductVariant.objects.create(
            title="Test Variant 1", product=product, size=size_1, price=10)
        ProductVariant.objects.create(
            title="Test Variant 2", product=product, size=size_2, price=20)
        variants = ProductVariant.objects.all()

        self.assertQuerysetEqual(list(product.get_product_variants), variants)
        self.assertEqual(len(variants), len(product.get_product_variants))
