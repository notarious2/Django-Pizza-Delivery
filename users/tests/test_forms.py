from users.forms import UserRegisterForm
from django.test import TestCase


class TestUserCreationForm(TestCase):
    """Test user creation form"""

    def test_customer_creation_valid_data(self):
        """Test customer creation with valid data"""
        form = UserRegisterForm(
            {
                "email": "test@example.com",
                "username": "testuser",
                "password1": "TestTest123#",
                "password2": "TestTest123#",
            }
        )
        self.assertTrue(form.is_valid())

    def test_customer_creation_invalid_data(self):
        """Test customer creation with invalid data"""
        form = UserRegisterForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 4)
