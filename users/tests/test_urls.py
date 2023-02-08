from django.test import SimpleTestCase
from django.urls import reverse, resolve
from users.views import SignUpView, MyLoginView, logout_view, my_orders


class TestUserUrls(SimpleTestCase):
    """Test that User URLs are resolved"""

    def test_register_url_is_resolved(self):
        """Test register url is resolved"""
        url = reverse("users:register")
        self.assertEqual(resolve(url).func.view_class, SignUpView)

    def test_login_url_is_resolved(self):
        """Test login url is resolved"""
        url = reverse("users:login")
        self.assertEqual(resolve(url).func.view_class, MyLoginView)

    def test_logout_url_is_resolved(self):
        """Test logout url is resolved"""
        url = reverse("users:logout")
        self.assertEqual(resolve(url).func, logout_view)

    def test_my_orders_url_is_resolved(self):
        """Test My Orders url is resolved"""
        url = reverse("users:my_orders")
        self.assertEqual(resolve(url).func, my_orders)
