from django.test import TestCase, Client
from django.urls import reverse
from django.http.cookie import SimpleCookie
from order.models import Order, OrderItem, Coupon
from store.models import Product
from users.models import Customer
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
import datetime
from django.contrib.messages import get_messages
from django.conf import settings
from unittest import skipIf

stipe_coupon_id = settings.STRIPE_COUPON_ID_PERCENT


class TestPercentCouponViews(TestCase):
    """Test Apply and Remove Functions for a Guest user"""

    @classmethod
    def setUpTestData(cls):
        # create a guest user
        cls.customer, created = Customer.objects.get_or_create(
            device="TestDeviceId")
        # create a product and add to customer's order
        with open("functional_tests/test_image.jpg", "rb") as image:
            image = SimpleUploadedFile(
                "test_image.jpg", image.read(), content_type="image/jpg")

        cls.product = Product.objects.create(
            name='Test Product', price=15, image=image)
        cls.order = Order.objects.create(customer=cls.customer)
        cls.order_item = OrderItem.objects.create(
            product=cls.product, order=cls.order, quantity=10)

        # Create a Coupon
        now = timezone.now()
        tom = timezone.make_aware(
            datetime.datetime.now() + datetime.timedelta(days=1))

        cls.coupon = Coupon.objects.create(
            code='TestCodePercent',
            active=True,
            discount_type='Percent',
            discount_amount=20,
            valid_from=now,
            valid_to=tom,  # stripe_coupon_id='LlHQL2lT'
        )

        cls.coupon_verified = Coupon.objects.create(
            code='winter',
            active=True,
            discount_type='Percent',
            discount_amount=50,
            valid_from=now,
            valid_to=tom,
            stripe_coupon_id=stipe_coupon_id
        )

    def setUp(self):
        self.client = Client()
        # set test cookies
        self.client.cookies = SimpleCookie({'device': 'TestDeviceId'})
        self.add_coupon_url = reverse('order:add-coupon')
        self.remove_coupon_url = reverse('order:remove-coupon')

    def tearDown(self):
        # delete test image from media folder
        self.product.image.delete()

    def test_coupon_apply_invalid_form(self):
        """Test apply coupon entered code is invalid """

        data = {
            'code': 'ToooooooooooLoooooooooooooooooooooooooooooooooooooooooooooooooooong'}
        response = self.client.post(self.add_coupon_url, data, format='json')

        all_messages = [msg for msg in get_messages(response.wsgi_request)]
        message = all_messages[0].message
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('order:checkout'))
        self.assertEqual(message, 'Coupon code is invalid')

    def test_coupon_apply_does_not_exist(self):
        """Test apply coupon does not exist """

        data = {'code': 'NotExistingCode'}
        response = self.client.post(self.add_coupon_url, data, format='json')

        all_messages = [msg for msg in get_messages(response.wsgi_request)]
        message = all_messages[0].message
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('order:checkout'))
        self.assertEqual(message, 'Coupon does not exist')

    def test_coupon_apply_exists_but_not_verified(self):
        """Test apply coupon exists but not verified by Stripe webhook"""

        data = {'code': 'TestCodePercent'}
        response = self.client.post(self.add_coupon_url, data, format='json')

        all_messages = [msg for msg in get_messages(response.wsgi_request)]
        message = all_messages[0].message

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('order:checkout'))
        self.assertEqual(message, 'Coupon cannot be verified')

    @skipIf(not stipe_coupon_id, "could not find Stripe Coupon ID")
    def test_coupon_apply_success(self):
        """Test apply coupon succeeds - Skips the test if """

        data = {'code': 'Winter'}
        response = self.client.post(self.add_coupon_url, data, format='json')

        all_messages = [msg for msg in get_messages(response.wsgi_request)]
        message = all_messages[0].message
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('order:checkout'))
        self.assertEqual(message, 'Coupon applied')

    def test_remove_coupon(self):
        """Removing coupon from order"""

        # add coupon to the order
        self.order.coupon = self.coupon
        self.order.save()
        # make sure order has a coupon before request
        self.assertIsNotNone(Order.objects.filter(
            customer=self.customer)[0].coupon)

        response = self.client.post(self.remove_coupon_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('order:checkout'))
        # no coupon afterwards
        self.assertIsNone(Order.objects.filter(
            customer=self.customer)[0].coupon)
