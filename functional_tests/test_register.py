import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from users.models import User
from time import sleep


class TestCustomerRegistration(StaticLiveServerTestCase):
    """Test Customer Registration"""

    def setUp(self):
        chromedriver_autoinstaller.install()
        options = webdriver.ChromeOptions()
        # to run without openning browser
        options.add_argument('headless')
        # to ignore errors in terminal
        options.add_experimental_option(
            'excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=options)

        self.register_url = self.live_server_url + reverse('users:register')
        self.login_url = self.live_server_url + reverse('users:login')

    def tearDown(self):
        self.driver.close()

    def test_customer_registration(self):
        """Test customer registration"""

        self.driver.get(self.register_url)

        email = self.driver.find_element(By.NAME, 'email')
        username = self.driver.find_element(By.NAME, 'username')
        password1 = self.driver.find_element(By.NAME, 'password1')
        password2 = self.driver.find_element(By.NAME, 'password2')

        email.send_keys('test@example.com')
        username.send_keys('testuser')
        password1.send_keys('TestUserPassword123#')
        password2.send_keys('TestUserPassword123#')

        self.driver.find_element(By.ID, 'register-button').click()

        self.assertEqual(self.driver.current_url, self.login_url)

    def test_customer_create_fails_if_username_exists(self):
        """Test that customer creation fails if username already exists"""
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword')

        self.driver.get(self.register_url)

        email = self.driver.find_element(By.NAME, 'email')
        username = self.driver.find_element(By.NAME, 'username')
        password1 = self.driver.find_element(By.NAME, 'password1')
        password2 = self.driver.find_element(By.NAME, 'password2')

        email.send_keys('test2@example.com')
        username.send_keys('testuser')
        password1.send_keys('VeryStrongpassWord123#')
        password2.send_keys('VeryStrongpassWord123#')

        self.driver.find_element(By.ID, 'register-button').click()
        get_source = self.driver.page_source

        self.assertIn('A user with that username already exists', get_source)

    def test_customer_create_fails_if_email_exists(self):
        """Test that customer creation fails if email already exists"""
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword')

        self.driver.get(self.register_url)

        email = self.driver.find_element(By.NAME, 'email')
        username = self.driver.find_element(By.NAME, 'username')
        password1 = self.driver.find_element(By.NAME, 'password1')
        password2 = self.driver.find_element(By.NAME, 'password2')

        username.send_keys('testuser2')
        email.send_keys('test@example.com')
        password1.send_keys('VeryStrongpassWord123#')
        password2.send_keys('VeryStrongpassWord123#')

        self.driver.find_element(By.ID, 'register-button').click()
        get_source = self.driver.page_source

        self.assertIn('User with this Email already exists', get_source)
