from django.test import TestCase
from order.models import Order, OrderItem, Coupon, PickUpDetail, ShippingAddress
from users.models import Customer, User
from store.models import Product, Size, ProductVariant
import datetime
from django.utils import timezone
from decimal import Decimal


def create_guest_customer():
    return Customer.objects.create(device='test_device')


def create_registered_customer():
    user = User.objects.create_user(
        email="user@example.com", username="testuser")
    # must assign username or device to avoid error in string representation
    return Customer.objects.create(user=user)


def create_test_product(name="test product", price=12):
    return Product.objects.create(name=name, price=price)


def create_test_product_with_variants():
    """"Create test product with two variants"""
    product = Product.objects.create(name="Test Product with Variants")
    size_1 = Size.objects.create(name='Test Size 1')
    size_2 = Size.objects.create(name='Test Size 2')
    ProductVariant.objects.create(
        title="Test Variant 1", product=product, size=size_1, price=50)
    ProductVariant.objects.create(
        title="Test Variant 2", product=product, size=size_2, price=100)
    return product


class TestOrderModelsGuest(TestCase):
    """Test order and order item models for guest user"""

    def test_create_order_by_guest(self):
        """Test order creation by guest customer"""
        customer = create_guest_customer()
        order = Order.objects.create(customer=customer)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(str(order), f"{order.transaction_id} by {customer}")

    def test_create_order_item_guest_no_variants(self):
        """
        Order item creation by guest customer of a product without variation
        """
        customer = create_guest_customer()
        product = create_test_product()
        order = Order.objects.create(customer=customer)
        order_item = OrderItem.objects.create(
            product=product, order=order, quantity=1)

        self.assertEqual(OrderItem.objects.count(), 1)
        self.assertEqual(order_item.product, product)
        self.assertEqual(order_item.order, order)
        self.assertEqual(order_item.order.customer, customer)
        self.assertEqual(
            str(order_item), f"{product.name} #{order_item.quantity}")

    def test_create_order_item_guest_with_variants(self):
        """Order item creation by guest customer of a product with product variants"""
        customer = create_guest_customer()
        order = Order.objects.create(customer=customer)
        product_with_variants = create_test_product_with_variants()
        first_variant = ProductVariant.objects.all()[0]
        order_item = OrderItem.objects.create(
            product=product_with_variants, variation=first_variant, order=order, quantity=1)

        self.assertEqual(OrderItem.objects.count(), 1)
        self.assertEqual(order_item.product, product_with_variants)
        self.assertEqual(order_item.order, order)
        self.assertEqual(order_item.variation, first_variant)
        self.assertEqual(order_item.order.customer, customer)

    def test_order_item_properties_guest_no_variation(self):
        """Test order item properties of a product without variation for guest user"""
        customer = create_guest_customer()
        product = create_test_product()
        order = Order.objects.create(customer=customer)
        order_item = OrderItem.objects.create(
            product=product, order=order, quantity=2)

        self.assertEqual(order_item.get_item_price, 12)
        self.assertEqual(order_item.get_total, 24)

    def test_order_item_properties_guest_with_variation(self):
        """Test order item properties of a product without variation for guest user"""
        customer = create_guest_customer()
        product = create_test_product_with_variants()
        first_variant = ProductVariant.objects.filter(
            title='Test Variant 1')[0]
        order = Order.objects.create(customer=customer)
        order_item = OrderItem.objects.create(
            product=product, variation=first_variant, order=order, quantity=2)

        self.assertEqual(order_item.get_item_price, Decimal('50'))
        self.assertEqual(order_item.get_total, Decimal('100'))

    def test_order_properties_no_coupon_no_variants_guest(self):
        """Test order of a product without variants and without coupon properties for guest"""
        customer = create_guest_customer()
        product_1 = create_test_product()
        product_2 = create_test_product(name="Test product 2", price=10)
        order = Order.objects.create(customer=customer)
        order_item_1 = OrderItem.objects.create(
            product=product_1, order=order, quantity=1)
        order_item_2 = OrderItem.objects.create(
            product=product_2, order=order, quantity=2)

        self.assertEqual(order.get_cart_subtotal, 32)
        self.assertEqual(order.get_cart_items, 3)
        self.assertEqual(order.get_cart_total, order.get_cart_subtotal)
        self.assertEqual(order.get_coupon_value, None)
        self.assertIn("Test product", order.display_items)
        self.assertIn("Test product 2", order.display_items)

    def test_order_properties_no_coupon_with_variants_guest(self):
        """Test order of a product with variants and without coupon properties for guest"""
        customer = create_guest_customer()
        product = create_test_product_with_variants()
        product_variant_1 = ProductVariant.objects.filter(
            title="Test Variant 1")[0]
        product_variant_2 = ProductVariant.objects.filter(
            title="Test Variant 2")[0]
        order = Order.objects.create(customer=customer)
        OrderItem.objects.create(
            product=product, variation=product_variant_1, order=order, quantity=1)
        OrderItem.objects.create(
            product=product, variation=product_variant_2, order=order, quantity=2)

        self.assertEqual(order.get_cart_subtotal, Decimal(250))
        self.assertEqual(order.get_cart_items, 3)
        self.assertEqual(order.get_cart_total, order.get_cart_subtotal)
        self.assertEqual(order.get_coupon_value, None)
        self.assertIn("Test Size 1", order.display_items)
        self.assertIn("Test Size 2", order.display_items)

    def test_order_properties_with_percent_coupon_guest(self):
        """Test order with applied percent coupon for guest"""
        customer = create_guest_customer()
        product_1 = create_test_product(name="Test product 1", price=5)
        product_2 = create_test_product(name="Test product 2", price=3)
        order = Order.objects.create(customer=customer)
        order_item_1 = OrderItem.objects.create(
            product=product_1, order=order, quantity=2)
        order_item_2 = OrderItem.objects.create(
            product=product_2, order=order, quantity=1)

        now = timezone.now()
        tom = timezone.make_aware(
            datetime.datetime.now() + datetime.timedelta(days=1))

        coupon = Coupon.objects.create(
            code='TestCodePercent',
            active=True,
            discount_type='Percent',
            discount_amount=20,
            valid_from=now,
            valid_to=tom)

        order.coupon = coupon
        self.assertEqual(order.get_cart_subtotal, 13)
        self.assertEqual(order.get_cart_items, 3)
        self.assertEqual(order.get_coupon_value, Decimal(str(13*.2)))
        self.assertEqual(order.get_cart_total, Decimal(str(13*.8)))

    def test_order_properties_with_absolute_coupon_guest(self):
        """Test order with applied absolute coupon for guest"""
        customer = create_guest_customer()
        product_1 = create_test_product(name="Test product 1", price=5)
        product_2 = create_test_product(name="Test product 2", price=3)
        order = Order.objects.create(customer=customer)
        order_item_1 = OrderItem.objects.create(
            product=product_1, order=order, quantity=2)
        order_item_2 = OrderItem.objects.create(
            product=product_2, order=order, quantity=1)

        now = timezone.now()
        tom = timezone.make_aware(
            datetime.datetime.now() + datetime.timedelta(days=1))

        coupon = Coupon.objects.create(
            code='TestCodePercent',
            active=True,
            discount_type='Absolute',
            discount_amount=10,
            valid_from=now,
            valid_to=tom)

        order.coupon = coupon
        self.assertEqual(order.get_cart_subtotal, 13)
        self.assertEqual(order.get_cart_items, 3)
        self.assertEqual(order.get_coupon_value, 10)
        self.assertEqual(order.get_cart_total, 3)


class TestOrderModelsRegisteredUser(TestCase):
    """Test order and orderitem models for registered user"""

    def test_create_order_by_customer(self):
        """Test order creation by registered customer"""

        customer = create_registered_customer()
        order = Order.objects.create(customer=customer)
        self.assertEqual(order.customer.user.username, 'testuser')
        self.assertEqual(order.customer, customer)
        self.assertEqual(str(order), f"{order.transaction_id} by {customer}")

    def test_create_order_item_by_customer_no_variants(self):
        """Order item creation of product without variants by registered user"""
        customer = create_registered_customer()
        product = create_test_product()
        order = Order.objects.create(customer=customer)
        order_item = OrderItem.objects.create(
            product=product, order=order, quantity=1)

        self.assertEqual(OrderItem.objects.count(), 1)
        self.assertEqual(order_item.product, product)
        self.assertEqual(order_item.order, order)
        self.assertEqual(order_item.order.customer, customer)

    def test_create_order_item_guest_with_variants(self):
        """Order item creation of a product with variants by a registered user """
        customer = create_registered_customer()
        order = Order.objects.create(customer=customer)
        product_with_variants = create_test_product_with_variants()
        first_variant = ProductVariant.objects.all()[0]
        order_item = OrderItem.objects.create(
            product=product_with_variants, variation=first_variant, order=order, quantity=1)

        self.assertEqual(OrderItem.objects.count(), 1)
        self.assertEqual(order_item.product, product_with_variants)
        self.assertEqual(order_item.order, order)
        self.assertEqual(order_item.variation, first_variant)
        self.assertEqual(order_item.order.customer, customer)

    def test_order_item_properties_customer(self):
        """Test order item properties for a registered user"""
        customer = create_registered_customer()
        product = create_test_product()
        order = Order.objects.create(customer=customer)
        order_item = OrderItem.objects.create(
            product=product, order=order, quantity=2)

        self.assertEqual(order_item.get_item_price, 12)
        self.assertEqual(order_item.get_total, 24)

    def test_order_item_properties_customer_with_variation(self):
        """Test order item properties of a product without variation for a registered user"""
        customer = create_registered_customer()
        product = create_test_product_with_variants()
        first_variant = ProductVariant.objects.filter(
            title='Test Variant 1')[0]
        order = Order.objects.create(customer=customer)
        order_item = OrderItem.objects.create(
            product=product, variation=first_variant, order=order, quantity=2)

        self.assertEqual(order_item.get_item_price, Decimal('50'))
        self.assertEqual(order_item.get_total, Decimal('100'))

    def test_order_properties_no_coupon_without_variants_customer(self):
        """Test order of product without variatns and no coupon properties for a registered user"""
        customer = create_registered_customer()
        product_1 = create_test_product()
        product_2 = create_test_product(name="Test product 2", price=10)
        order = Order.objects.create(customer=customer)
        order_item_1 = OrderItem.objects.create(
            product=product_1, order=order, quantity=1)
        order_item_2 = OrderItem.objects.create(
            product=product_2, order=order, quantity=2)

        self.assertEqual(order.get_cart_subtotal, 32)
        self.assertEqual(order.get_cart_items, 3)
        self.assertEqual(order.get_cart_total, order.get_cart_subtotal)
        self.assertEqual(order.get_coupon_value, None)

    def test_order_properties_no_coupon_with_variants_customer(self):
        """Test order of a product with variants and without coupon properties for a registered user"""
        customer = create_registered_customer()
        product = create_test_product_with_variants()
        product_variant_1 = ProductVariant.objects.filter(
            title="Test Variant 1")[0]
        product_variant_2 = ProductVariant.objects.filter(
            title="Test Variant 2")[0]
        order = Order.objects.create(customer=customer)
        OrderItem.objects.create(
            product=product, variation=product_variant_1, order=order, quantity=1)
        OrderItem.objects.create(
            product=product, variation=product_variant_2, order=order, quantity=2)

        self.assertEqual(order.get_cart_subtotal, Decimal(250))
        self.assertEqual(order.get_cart_items, 3)
        self.assertEqual(order.get_cart_total, order.get_cart_subtotal)
        self.assertEqual(order.get_coupon_value, None)

    def test_order_properties_with_percent_coupon_customer(self):
        """Test order with applied percent coupon for registered user"""
        customer = create_registered_customer()
        product_1 = create_test_product(name="Test product 1", price=5)
        product_2 = create_test_product(name="Test product 2", price=3)
        order = Order.objects.create(customer=customer)
        order_item_1 = OrderItem.objects.create(
            product=product_1, order=order, quantity=2)
        order_item_2 = OrderItem.objects.create(
            product=product_2, order=order, quantity=1)

        now = timezone.now()
        tom = timezone.make_aware(
            datetime.datetime.now() + datetime.timedelta(days=1))

        coupon = Coupon.objects.create(
            code='TestCodePercent',
            active=True,
            discount_type='Percent',
            discount_amount=20,
            valid_from=now,
            valid_to=tom)

        order.coupon = coupon
        self.assertEqual(order.get_cart_subtotal, 13)
        self.assertEqual(order.get_cart_items, 3)
        self.assertEqual(order.get_coupon_value, Decimal(str(13*.2)))
        self.assertEqual(order.get_cart_total, Decimal(str(13*.8)))

    def test_order_properties_with_absolute_coupon_customer(self):
        """Test order with applied absolute coupon for registered user"""
        customer = create_registered_customer()
        product_1 = create_test_product(name="Test product 1", price=5)
        product_2 = create_test_product(name="Test product 2", price=3)
        order = Order.objects.create(customer=customer)
        order_item_1 = OrderItem.objects.create(
            product=product_1, order=order, quantity=2)
        order_item_2 = OrderItem.objects.create(
            product=product_2, order=order, quantity=1)

        now = timezone.now()
        tom = timezone.make_aware(
            datetime.datetime.now() + datetime.timedelta(days=1))

        coupon = Coupon.objects.create(
            code='TestCodePercent',
            active=True,
            discount_type='Absolute',
            discount_amount=10,
            valid_from=now,
            valid_to=tom)

        order.coupon = coupon
        self.assertEqual(order.get_cart_subtotal, 13)
        self.assertEqual(order.get_cart_items, 3)
        self.assertEqual(order.get_coupon_value, 10)
        self.assertEqual(order.get_cart_total, 3)


class TestOrderModels(TestCase):
    """
    Test Coupon, ShippingAddress and PickUpDetail
    models for registered user
    """

    def test_create_coupon_percent(self):
        """Test creation of a coupon with percent discount"""
        now = timezone.now()
        tom = timezone.make_aware(
            datetime.datetime.now() + datetime.timedelta(days=1))

        coupon = Coupon.objects.create(
            code='TestCodePercent',
            active=True,
            discount_type='Percent',
            discount_amount=20,
            valid_from=now,
            valid_to=tom)

        self.assertEqual(Coupon.objects.count(), 1)
        self.assertTrue(coupon.active)
        self.assertEqual(coupon.code, 'TestCodePercent')
        self.assertEqual(coupon.discount_type, 'Percent')
        self.assertEqual(
            str(coupon), "TestCodePercent type: Percent value: 20")

    def test_create_coupon_absolute(self):
        """Test creation of a coupon with percent discount"""

        now = timezone.now()
        tom = timezone.make_aware(
            datetime.datetime.now() + datetime.timedelta(days=1))

        coupon = Coupon.objects.create(
            code='TestCodeAbs',
            active=True,
            discount_type='Absolute',
            discount_amount=10,
            valid_from=now,
            valid_to=tom)

        self.assertEqual(Coupon.objects.count(), 1)
        self.assertTrue(coupon.active)
        self.assertEqual(coupon.code, 'TestCodeAbs')
        self.assertEqual(coupon.discount_type, 'Absolute')
        self.assertEqual(str(coupon), "TestCodeAbs type: Absolute value: 10")

    def test_create_pickup_asap(self):
        """Test create PickUpDetail model with ugency=asap"""
        pickup = PickUpDetail.objects.create(urgency='asap')

        self.assertEqual(PickUpDetail.objects.count(), 1)
        self.assertEqual(str(pickup), 'asap')

    def test_create_pickup_custom(self):
        """Test create PickUpDetail model with ugency=custom"""
        now = timezone.now()
        pickup = PickUpDetail.objects.create(urgency='custom', pickup_date=now)

        self.assertEqual(PickUpDetail.objects.count(), 1)
        self.assertEqual(pickup.pickup_date, now)
        self.assertEqual(str(pickup), 'custom')

    def test_create_shipping_address(self):
        """Test creation of ShippingAddress model"""

        shipping = ShippingAddress.objects.create(
            first_name='First name',
            last_name='Last name',
            address_1='Address 1',
            city='City',
            state='State',
            country='County')
        self.assertEqual(
            str(shipping), f"{shipping.first_name} {shipping.last_name} {shipping.address_1}")
        self.assertEqual(ShippingAddress.objects.count(), 1)
