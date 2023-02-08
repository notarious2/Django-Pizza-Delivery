from django.test import TestCase
from users.models import User, Customer


class TestCustomerCreation(TestCase):
    """Test creation of a customer"""

    def setUp(self):
        self.credentials = {
            "email": "test@example.com",
            "username": "testuser",
        }

    def test_create_customer(self):
        user = User.objects.create_user(**self.credentials)
        customer = Customer.objects.create(user=user)

        self.assertEqual(customer.user, user)
        self.assertEqual(customer.user.username, self.credentials["username"])
