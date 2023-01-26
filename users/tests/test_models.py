from django.test import TestCase, Client
from users.models import User
from django.contrib.auth import get_user
from users.models import Customer


class TestCustomerCreation(TestCase):
    """Test creation of a customer"""

    def setUp(self):
        self.credentials = {
            'email': 'test@example.com',
            'username': 'testuser',
        }

    def test_create_customer(self):
        user = User.objects.create_user(**self.credentials)
        customer = Customer.objects.create(user=user)

        self.assertEqual(customer.user, user)
        self.assertEqual(customer.user.username, self.credentials['username'])
