from django.test import TestCase, Client
from django.urls import reverse
from store.models import Product
from django.core.files.uploadedfile import SimpleUploadedFile


class TestStoreViews(TestCase):
    """Test views in Store app"""

    def setUp(self):
        self.client = Client()

    def test_products_view_GET(self):
        """Test GET response in products view"""
        response = self.client.get(reverse('store:products'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/products.html')
        self.assertIn('products', response.context)
        self.assertIn('search_string', response.context)

    def test_product_search_text_GET_no_product(self):
        """Test GET response in products searched for unexisting product"""
        url = reverse('store:products') + '?product=TestProduct'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['search_string'], 'TestProduct')

    def test_pizzas_view_GET(self):
        """Test GET response in pizzas view"""
        response = self.client.get(reverse('store:pizzas'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/pizzas.html')
        self.assertIn('products', response.context)

    def test_drinks_view_GET(self):
        """Test GET response in drinks view"""
        response = self.client.get(reverse('store:drinks'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/drinks.html')
        self.assertIn('products', response.context)

    def test_sides_view_GET(self):
        """Test GET response in sides view"""
        response = self.client.get(reverse('store:sides'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/sides.html')
        self.assertIn('products', response.context)
