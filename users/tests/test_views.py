from django.test import TestCase, Client
from django.urls import reverse
from users.views import SignUpView, MyLoginView, logout_view, my_orders
from django.contrib.auth.models import User


class TestUserViews(TestCase):
    """Test views in users app"""

    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('users:register')
        self.login_url = reverse('users:login')
        self.credentials = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        User.objects.create_user(**self.credentials)

    def test_signup_view_GET(self):
        """Test get response in SignUpView"""

        response = self.client.get(self.signup_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_login_view_GET(self):
        """Test get response in MyLoginView"""

        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_login(self):
        """Test user login"""
        response = self.client.post(
            self.login_url, self.credentials, follow=True)
        self.assertTrue(response.context['user'].is_active)
        self.assertEqual(
            response.context['user'].username, self.credentials['username'])
