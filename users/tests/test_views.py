from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user
from users.models import Customer, User
from users.forms import UserRegisterForm
import json


class TestUserViews(TestCase):
    """Test views in users app"""

    def setUp(self):
        self.client = Client()
        self.signup_url = reverse("users:register")
        self.login_url = reverse("users:login")
        self.logout_url = reverse("users:logout")
        self.products_url = reverse("store:products")
        self.my_orders_url = reverse("users:my_orders")
        self.credentials = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword",
        }
        User.objects.create_user(**self.credentials)

    def test_signup_view_GET(self):
        """Test get response in SignUpView"""

        response = self.client.get(self.signup_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/register.html")

    def test_login_view_GET(self):
        """Test get response in MyLoginView"""

        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/login.html")

    def test_login_with_incorrect_email(self):
        """Test user login with incorrect email"""
        response = self.client.post(
            self.login_url,
            {"username": "incorrect@example.com", "password": "testpassword"},
            follow=True,
        )

        self.assertFalse(response.context["user"].is_authenticated)

    def test_login_with_email(self):
        """Test user login with email"""
        response = self.client.post(
            self.login_url,
            {"username": "test@example.com", "password": "testpassword"},
            follow=True,
        )
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertEqual(
            response.context["user"].username, self.credentials["username"]
        )

    def test_login_with_incorrect_username(self):
        """Test user login with incorrect username"""
        response = self.client.post(
            self.login_url,
            {"username": "IncorrectUsername", "password": "testpassword"},
            follow=True,
        )

        self.assertFalse(response.context["user"].is_authenticated)

    def test_login_with_username(self):
        """Test user login with username"""
        response = self.client.post(
            self.login_url,
            {"username": "testuser", "password": "testpassword"},
            follow=True,
        )
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertEqual(
            response.context["user"].username, self.credentials["username"]
        )

    def test_login_for_authenticated_user(self):
        """Test if authenticated user is redirected to main page"""
        self.client.login(**self.credentials)
        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.products_url)

    def test_logout_for_authenticated_user(self):
        """Test logout for authenticated user"""
        self.client.login(**self.credentials)

        # logout and check if redirected/redirected to the products page
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.products_url)

    def test_access_my_orders_for_customer(self):
        """Test logged-in customer can access my orders"""
        self.client.login(**self.credentials)
        user = get_user(self.client)
        Customer.objects.create(user=user)

        response = self.client.get(self.my_orders_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/orders.html")

    def test_access_my_orders_for_unauthenticated_user(self):
        """
        Test if unauthenticated user is redirected
        to the login page
        """
        response = self.client.get(self.my_orders_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url + f"?next={self.my_orders_url}")
