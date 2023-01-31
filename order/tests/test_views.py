from django.test import TestCase, Client
from django.urls import reverse
from django.http.cookie import SimpleCookie
from order.models import Order, OrderItem
from store.models import Product, ProductVariant, Size
from users.models import Customer
from decimal import Decimal
from django.core.files.uploadedfile import SimpleUploadedFile
import json


def create_test_product(name="test product", price=12):
    return Product.objects.create(name=name, price=price)


class TestOrderViewsGuest(TestCase):
    """Test views in order app for a guest user"""

    def setUp(self):
        self.client = Client()

    def test_cart_view_empty_redirected(self):
        """Test GET response to cart is redirect if no device cookie is set"""
        response = self.client.get(reverse('order:cart'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('store:products'))

    def test_cart_view_empty(self):
        """Test GET response in cart view after device cookie is set"""
        # set test cookies
        self.client.cookies = SimpleCookie({'device': 'TestDeviceId'})

        response = self.client.get(reverse('order:cart'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'order/cart.html')
        self.assertIn('order', response.context)
        self.assertIn('items', response.context)

        self.assertIsNone(response.context['order'])
        self.assertIsNone(response.context['items'])

    def test_cart_view_not_empty(self):
        self.client.cookies = SimpleCookie({'device': 'TestDeviceId'})
        customer, created = Customer.objects.get_or_create(
            device="TestDeviceId")
        # upload a test image
        with open("functional_tests/test_image.jpg", "rb") as image:
            image = SimpleUploadedFile(
                "test_image.jpg", image.read(), content_type="image/jpg")
        product = Product.objects.create(
            name='Test Product', price=10, image=image)
        order = Order.objects.create(customer=customer)
        order_item = OrderItem.objects.create(
            product=product, order=order, quantity=1)
        response = self.client.get(reverse('order:cart'))
        # delete test image from media folder
        product.image.delete()

        self.assertEqual(response.context['cart_quantity'], 1)
        self.assertEqual(response.context['order'], order)
        self.assertEqual(response.context['items'][0], order_item)

    def test_add_to_cart_post(self):
        """Test add to cart Product without Variation view with POST request"""
        self.client.cookies = SimpleCookie({'device': 'TestDeviceId'})
        # upload a test image
        with open("functional_tests/test_image.jpg", "rb") as image:
            image = SimpleUploadedFile(
                "test_image.jpg", image.read(), content_type="image/jpg")
        product = Product.objects.create(
            name='Test Product', price=10, image=image)
        url = reverse('order:add_to_cart', args=[product.pk])
        response = self.client.post(
            url, data=json.dumps({'quantity': '1'}), content_type='application/json')
        product.image.delete()

        customer_qs = Customer.objects.filter(device='TestDeviceId')
        # check that customer exists
        self.assertTrue(customer_qs.exists())
        customer = customer_qs[0]
        self.assertEqual(response.status_code, 200)
        # check that order with test customer exists
        self.assertTrue(Order.objects.filter(customer=customer).exists())
        # check that order item with test product exists
        self.assertTrue(OrderItem.objects.filter(product=product).exists())

        # check returned add to cart value
        # convert bytes to dictionary
        content = response.content
        content = json.loads(content.decode('utf-8'))
        self.assertEqual(content['cart_total'], 1)

    def test_add_to_cart_post_redirected(self):
        """Test add to cart view with POST request as device cookie is not set"""
        # upload a test image
        with open("functional_tests/test_image.jpg", "rb") as image:
            image = SimpleUploadedFile(
                "test_image.jpg", image.read(), content_type="image/jpg")
        product = Product.objects.create(
            name='Test Product', price=10, image=image)
        url = reverse('order:add_to_cart', args=[product.pk])
        response = self.client.post(
            url, data=json.dumps({'quantity': '1'}), content_type='application/json')
        product.image.delete()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('store:products'))

    def test_add_to_cart_variation_post(self):
        """Test add to cart Product with Variation view with POST request"""
        self.client.cookies = SimpleCookie({'device': 'TestDeviceId'})
        # upload a test image
        with open("functional_tests/test_image.jpg", "rb") as image:
            image = SimpleUploadedFile(
                "test_image.jpg", image.read(), content_type="image/jpg")

        # create a product with two variants
        product = Product.objects.create(
            name='Test Product', price=10, image=image)
        size_1 = Size.objects.create(name='Test Size 1')
        size_2 = Size.objects.create(name='Test Size 2')
        ProductVariant.objects.create(
            title="Test Variant 1", product=product, size=size_1, price=10)
        ProductVariant.objects.create(
            title="Test Variant 2", product=product, size=size_2, price=20)

        url = reverse('order:add_to_cart', args=[product.pk])
        response = self.client.post(
            url, data=json.dumps({'quantity': '2', 'size': 'Test Size 1'}), content_type='application/json')
        product.image.delete()
        # check returned add to cart value
        # convert bytes to dictionary
        content = response.content
        content = json.loads(content.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['cart_total'], 2)
