from django.test import TestCase, Client
from django.urls import reverse
from django.http.cookie import SimpleCookie
from order.models import Order, OrderItem
from store.models import Product
from users.models import Customer
from django.db.models import signals
import factory


class TestPaymentViewGuest(TestCase):
    """Test success payment view for Guest user"""

    def setUp(self):
        self.client = Client()
        # set test cookies
        self.client.cookies = SimpleCookie({"device": "TestDeviceId"})

    def test_access_success_failed_direct_access(self):
        """Test that success page is unavailable if accessed outside of cash and stripe checkout views"""
        response = self.client.get(reverse("order:success"))

        self.assertEqual(response.status_code, 404)

    def test_access_payment_success_from_cash_session(self):
        """Test that success page is accessed from cash checkout page"""
        referer_url = "checkout"  # cash checkout is referred from checkout view
        url = reverse("order:success") + "?cash=true"
        response = self.client.get(url, HTTP_REFERER=referer_url)

        self.assertTrue(response.status_code, 200)

    def test_access_payment_success_from_stripe_without_sessionid(self):
        """
        Test that success page is cannot be accessed from Stripe
        /create checkout session view for if no session id is passed in url
        """
        session = self.client.session
        session["redirected"] = True
        session.save()
        # ?session_id=TEST_SESSION_ID' is not passed
        url = reverse("order:success")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_access_payment_success_from_stripe_without_valid_delivery(self):
        """
        Test that success page is accessed from Stripe/create checkout session view
        without valid delivery option
        """
        # create customer
        customer, created = Customer.objects.get_or_create(device="TestDeviceId")

        # create a product without variants (test image is not needed)
        product = Product.objects.create(name="Test Product", price=15)

        # create order for guest user
        order = Order.objects.create(customer=customer)
        order_items = OrderItem.objects.create(
            order=order, product=product, quantity=10
        )
        order.delivery_method = "invalidDelivery"
        order.save()

        # add redirected session variable
        session = self.client.session
        session["redirected"] = True
        session.save()
        # pass test session id in url
        url = reverse("order:success") + "?session_id=TEST_SESSION_ID"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    @factory.django.mute_signals(signals.pre_save, signals.post_save)
    def test_access_payment_success_from_stripe_delivery(self):
        """
        Test that success page is accessed from Stripe/create checkout session view
        for delivery order
        """
        # create customer
        customer, created = Customer.objects.get_or_create(device="TestDeviceId")

        # create a product without variants (test image is not needed)
        product = Product.objects.create(name="Test Product", price=15)

        # create order for guest user
        order = Order.objects.create(customer=customer)
        order_items = OrderItem.objects.create(
            order=order, product=product, quantity=10
        )
        order.delivery_method = "delivery"
        order.save()

        # add shipping details to session
        session = self.client.session
        session["first_name"] = "first name"
        session["last_name"] = "last name"
        session["address_1"] = "address 1"
        session["city"] = "city"
        session["state"] = "state"
        session["country"] = "country"

        # add redirected session variable
        session["redirected"] = True
        session.save()
        # pass test session id in url
        url = reverse("order:success") + "?session_id=TEST_SESSION_ID"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.all()[0].delivery_method, "delivery")
        self.assertTrue(Order.objects.all()[0].complete)
        self.assertTrue(Order.objects.all()[0].paid)

    @factory.django.mute_signals(signals.pre_save, signals.post_save)
    def test_access_payment_success_from_stripe_carryout_asap(self):
        """
        Test that success page is accessed from Stripe/create checkout session view
        for carryout order with urgency='asap'
        """
        # create customer
        customer, created = Customer.objects.get_or_create(device="TestDeviceId")

        # create a product without variants (test image is not needed)
        product = Product.objects.create(name="Test Product", price=15)

        # create order for guest user
        order = Order.objects.create(customer=customer)
        order_items = OrderItem.objects.create(
            order=order, product=product, quantity=10
        )
        order.delivery_method = "carryout"
        order.save()

        # add shipping details to session
        session = self.client.session
        session["urgency"] = "asap"

        # add redirected session variable
        session["redirected"] = True
        session.save()
        # pass test session id in url
        url = reverse("order:success") + "?session_id=TEST_SESSION_ID"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.all()[0].delivery_method, "carryout")
        self.assertTrue(Order.objects.all()[0].complete)
        self.assertTrue(Order.objects.all()[0].paid)

    @factory.django.mute_signals(signals.pre_save, signals.post_save)
    def test_access_payment_success_from_stripe_carryout_custom(self):
        """
        Test that success page is accessed from Stripe/create checkout session view
        for carryout order with urgency='asap'
        """
        # create customer
        customer, created = Customer.objects.get_or_create(device="TestDeviceId")

        # create a product without variants (test image is not needed)
        product = Product.objects.create(name="Test Product", price=15)

        # create order for guest user
        order = Order.objects.create(customer=customer)
        order_items = OrderItem.objects.create(
            order=order, product=product, quantity=10
        )
        order.delivery_method = "carryout"
        order.save()

        # add shipping details to session
        session = self.client.session
        session["urgency"] = "custom"
        session["pickup_date"] = "2023-02-02 2:00 PM"

        # add redirected session variable
        session["redirected"] = True
        session.save()
        # pass test session id in url
        url = reverse("order:success") + "?session_id=TEST_SESSION_ID"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.all()[0].delivery_method, "carryout")
        self.assertTrue(Order.objects.all()[0].complete)
        self.assertTrue(Order.objects.all()[0].paid)

    def test_payment_cancel_fails_if_not_redirected(self):
        """Test that payment failed view unavailable if accessed directly"""

        response = self.client.get(reverse("order:failed"))
        self.assertEqual(response.status_code, 404)

    def test_payment_cancel_succeeds_if_redirected(self):
        """
        Test that payment failed view available if accessed from
        Stripe / create_checkout_session view
        """
        # mock session variable
        session = self.client.session
        session["redirected"] = True
        session.save()

        response = self.client.get(reverse("order:failed"))
        self.assertEqual(response.status_code, 200)
