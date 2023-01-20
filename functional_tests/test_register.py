from selenium import webdriver
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller

from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from users.models import Customer
import time


class TestCustomerRegistration(StaticLiveServerTestCase):
    """Test Customer Registration"""

    def setUp(self):
        chromedriver_autoinstaller.install()
        self.driver = webdriver.Chrome()

    def tearDown(self):
        self.driver.close()

    def test_customer_registration(self):
        """Test customer registration"""
        register_url = self.live_server_url + reverse('users:register')
        login_url = self.live_server_url + reverse('users:login')
        self.driver.get(register_url)
        email = self.driver.find_element(By.NAME, 'email')
        username = self.driver.find_element(By.NAME, 'username')
        password1 = self.driver.find_element(By.NAME, 'password1')
        password2 = self.driver.find_element(By.NAME, 'password2')

        email.send_keys('test@example.com')
        username.send_keys('testuser')
        password1.send_keys('TestUserPassword123#')
        password2.send_keys('TestUserPassword123#')

        button_selector = 'body > div > form > button'
        self.driver.find_element(By.CSS_SELECTOR, button_selector).click()

        self.assertEqual(self.driver.current_url, login_url)

    def test_customer_create_fails_if_username_exists(self):
        """Test that customer creation fails if username already exists"""
        user = User.objects.create_user(
            username='testuser', password='testpassword', email='test@example.com')

        register_url = self.live_server_url + reverse('users:register')
        self.driver.get(register_url)

        email = self.driver.find_element(By.NAME, 'email')
        username = self.driver.find_element(By.NAME, 'username')
        password1 = self.driver.find_element(By.NAME, 'password1')
        password2 = self.driver.find_element(By.NAME, 'password2')

        email.send_keys('test2@example.com')
        username.send_keys('testuser')
        password1.send_keys('VeryStrongpassWord123#')
        password2.send_keys('VeryStrongpassWord123#')

        button_selector = 'body > div > form > button'
        self.driver.find_element(By.CSS_SELECTOR, button_selector).click()
        get_source = self.driver.page_source

        self.assertIn('A user with that username already exists', get_source)
