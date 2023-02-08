from django.test import SimpleTestCase
from django.urls import reverse, resolve
from store.views import products, pizzas, drinks, sides


class TestStoreUrls(SimpleTestCase):
    """Test that Store URLs are resolved"""

    def test_products_url_is_resolved(self):
        """Test main page/products url is resolved"""
        url = reverse("store:products")
        self.assertEqual(resolve(url).func, products)

    def test_pizzas_url_is_resolved(self):
        """Test pizzas url is resolved"""
        url = reverse("store:pizzas")
        self.assertEqual(resolve(url).func, pizzas)

    def test_drinks_url_is_resolved(self):
        """Test drinks url is resolved"""
        url = reverse("store:drinks")
        self.assertEqual(resolve(url).func, drinks)

    def test_sides_url_is_resolved(self):
        """Test sides url is resolved"""
        url = reverse("store:sides")
        self.assertEqual(resolve(url).func, sides)
