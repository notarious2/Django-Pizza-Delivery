from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.auth import get_user
from users.models import Customer


class TestCustomerCreation(TestCase):
    """Test creation of a customer"""

    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        User.objects.create_user(**self.credentials)
        self.client = Client()

    def test_create_customer(self):
        self.client.login(**self.credentials)
        user = get_user(self.client)
        customer = Customer.objects.create(user=user)

        self.assertEqual(customer.user, user)
        self.assertEqual(customer.user.username, self.credentials['username'])
