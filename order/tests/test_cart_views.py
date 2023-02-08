from django.test import TestCase, Client
from django.urls import reverse
from django.http.cookie import SimpleCookie
from order.models import Order, OrderItem
from store.models import Product, ProductVariant, Size
from users.models import Customer
from django.core.files.uploadedfile import SimpleUploadedFile
import json


class TestCartViewsGuest(TestCase):
    """Test views ran on the main page for Guest user"""

    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.customer, created = Customer.objects.get_or_create(device="TestDeviceId")
        # upload a test image
        with open("functional_tests/test_image.jpg", "rb") as image:
            image = SimpleUploadedFile(
                "test_image.jpg", image.read(), content_type="image/jpg"
            )

        cls.product = Product.objects.create(name="Test Product", price=15, image=image)

        # create a product with 2 variants
        cls.product_with_variant = Product.objects.create(
            name="Test Product with Variant", image=image
        )
        size_1 = Size.objects.create(name="Test Size 1")
        size_2 = Size.objects.create(name="Test Size 2")
        cls.variant_1 = ProductVariant.objects.create(
            title="Test Variant 1",
            product=cls.product_with_variant,
            size=size_1,
            price=10,
        )
        cls.variant_2 = ProductVariant.objects.create(
            title="Test Variant 2",
            product=cls.product_with_variant,
            size=size_2,
            price=20,
        )

    def setUp(self):
        self.client_no_cookies = Client()
        self.client = Client()
        # set test cookies
        self.client.cookies = SimpleCookie({"device": "TestDeviceId"})

    def tearDown(self):
        self.product.image.delete()
        self.product_with_variant.image.delete()

    def test_cart_view_empty_redirected(self):
        """Test GET response to cart is redirect if no device cookie is set"""
        response = self.client_no_cookies.get(reverse("order:cart"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("store:products"))

    def test_cart_view_empty(self):
        """Test GET response in empty cart after device cookie is set"""

        response = self.client.get(reverse("order:cart"), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "order/cart.html")
        self.assertIn("order", response.context)
        self.assertIn("items", response.context)

        self.assertIsNone(response.context["order"])
        self.assertIsNone(response.context["items"])

    def test_cart_view_not_empty(self):
        """Test GET response in not empty cart after device cookie is set"""

        order = Order.objects.create(customer=self.customer)
        order_item = OrderItem.objects.create(
            product=self.product, order=order, quantity=1
        )

        response = self.client.get(reverse("order:cart"))

        self.assertEqual(response.context["cart_quantity"], 1)
        self.assertEqual(response.context["order"], order)
        self.assertEqual(response.context["items"][0], order_item)

    def test_add_to_cart_post(self):
        """Test add to cart Product w/o Variation with POST request"""

        url = reverse("order:add_to_cart", args=[self.product.pk])
        response = self.client.post(
            url, data=json.dumps({"quantity": "5"}), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        # check that order with test customer exists
        self.assertTrue(Order.objects.filter(customer=self.customer).exists())
        # check that order item with test product exists
        self.assertTrue(OrderItem.objects.filter(product=self.product).exists())
        # check returned add to cart value
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(content["cart_total"], 5)

    def test_add_to_cart_variation_post(self):
        """Test add to cart Product with Variation with POST request"""

        url = reverse("order:add_to_cart", args=[self.product_with_variant.pk])
        data = json.dumps({"quantity": "5", "size": "Test Size 1"})
        response = self.client.post(url, data=data, content_type="application/json")
        content = json.loads(response.content.decode("utf-8"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["cart_total"], 5)
        self.assertTrue(Order.objects.filter(customer=self.customer).exists())
        self.assertTrue(
            OrderItem.objects.filter(product=self.product_with_variant).exists()
        )

        # check variation in order item
        order = Order.objects.filter(customer=self.customer)[0]
        variation = OrderItem.objects.filter(order=order)[0].variation
        self.assertEqual(variation, self.variant_1)

    def test_add_to_cart_post_redirected(self):
        """Test add to cart gets redirected as device cookie is not set"""

        url = reverse("order:add_to_cart", args=[self.product.pk])
        response = self.client_no_cookies.post(
            url, data=json.dumps({"quantity": "1"}), content_type="application/json"
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("store:products"))


class TestCartViewsGuestInside(TestCase):
    """Test views ran inside the cart for Guest user"""

    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.customer, created = Customer.objects.get_or_create(device="TestDeviceId")
        # upload a test image
        with open("functional_tests/test_image.jpg", "rb") as image:
            image = SimpleUploadedFile(
                "test_image.jpg", image.read(), content_type="image/jpg"
            )

        cls.product = Product.objects.create(name="Test Product", price=15, image=image)
        cls.order = Order.objects.create(customer=cls.customer)
        cls.order_item = OrderItem.objects.create(
            product=cls.product, order=cls.order, quantity=10
        )

    def setUp(self):
        self.client = Client()
        self.client.cookies = SimpleCookie({"device": "TestDeviceId"})

    def tearDown(self):
        # delete test image from media folder
        self.product.image.delete()

    def test_remove_from_cart(self):
        """Test remove from cart inside the cart"""
        response = self.client.post(
            reverse("order:remove-from-cart", args=[self.order_item.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("order:cart"))
        self.assertEqual(OrderItem.objects.all().count(), 0)

    def test_increase_product_quantity(self):
        """Test increase product quantity by 1"""

        response = self.client.post(
            reverse("order:increase-product-quantity", args=[self.order_item.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("order:cart"))
        self.assertEqual(
            OrderItem.objects.filter(pk=self.order_item.pk)[0].quantity, 11
        )

    def test_reduce_product_quantity(self):
        """Test reduce product quantity by 1"""

        response = self.client.post(
            reverse("order:reduce-product-quantity", args=[self.order_item.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("order:cart"))
        self.assertEqual(OrderItem.objects.filter(pk=self.order_item.pk)[0].quantity, 9)

    def test_reduce_product_quantity_zero_left(self):
        """Test reduce product quantity by 1 removes OrderItem"""

        # update quantity of the order_item to 1
        self.order_item.quantity = 1
        self.order_item.save()

        response = self.client.post(
            reverse("order:reduce-product-quantity", args=[self.order_item.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("order:cart"))
        self.assertFalse(OrderItem.objects.filter(pk=self.order_item.pk).exists())

    def test_change_product_quantity_using_ajax(self):
        """Test change product quantity by specific number using ajax call"""

        url = reverse("order:change-product-quantity")
        data = {"quantity": "50", "orderItemId": self.order_item.pk}

        response = self.client.post(url, data, xhr=True)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("order:cart"))
        self.assertEqual(
            OrderItem.objects.filter(pk=self.order_item.pk)[0].quantity, 50
        )
