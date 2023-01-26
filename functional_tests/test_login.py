import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from users.models import User


class TestCustomerLogin(StaticLiveServerTestCase):
    """Test customer login in StaticLiverServer"""

    def setUp(self):
        chromedriver_autoinstaller.install()
        options = webdriver.ChromeOptions()
        # to run without openning browser
        options.add_argument('headless')
        # to ignore errors in terminal
        options.add_experimental_option(
            'excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=options)

        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',)

        # login and success url routes
        self.login_url = self.live_server_url + reverse('users:login')
        self.expected_url = self.live_server_url + reverse('store:products')

    def tearDown(self):
        self.driver.close()

    def test_login_with_valid_username(self):
        """Test user logs in with valid username"""
        self.driver.get(self.login_url)
        username = self.driver.find_element(By.NAME, 'username')
        password = self.driver.find_element(By.NAME, 'password')

        username.send_keys('testuser')
        password.send_keys('testpassword')

        self.driver.find_element(By.ID, 'login-button').click()

        self.assertEqual(self.driver.current_url, self.expected_url)

    def test_login_with_valid_email(self):
        """Test user logs in with valid email"""
        self.driver.get(self.login_url)

        username = self.driver.find_element(By.NAME, 'username')
        password = self.driver.find_element(By.NAME, 'password')

        username.send_keys('test@example.com')
        password.send_keys('testpassword')

        self.driver.find_element(By.ID, 'login-button').click()

        self.assertEqual(self.driver.current_url, self.expected_url)

    def test_login_with_invalid_username(self):
        """Test log in attempt with invalid username"""
        self.driver.get(self.login_url)

        username = self.driver.find_element(By.NAME, 'username')
        password = self.driver.find_element(By.NAME, 'password')

        username.send_keys('testwronguser')
        password.send_keys('testpassword')
        self.driver.find_element(By.ID, 'login-button').click()
        # get html page source
        get_source = self.driver.page_source

        self.assertIn('Invalid username or password', get_source)

    def test_login_with_invalid_email(self):
        """Test log in attempt with invalid email"""
        self.driver.get(self.login_url)

        username = self.driver.find_element(By.NAME, 'username')
        password = self.driver.find_element(By.NAME, 'password')

        username.send_keys('testwronguser@test.com')
        password.send_keys('testpassword')
        self.driver.find_element(By.ID, 'login-button').click()
        # get html page source
        get_source = self.driver.page_source

        self.assertIn('Invalid username or password', get_source)

    def test_login_with_invalid_password(self):
        """Test log in attempt with invalid email"""
        self.driver.get(self.login_url)

        username = self.driver.find_element(By.NAME, 'username')
        password = self.driver.find_element(By.NAME, 'password')

        username.send_keys('testuser')
        password.send_keys('wrongpassword')
        self.driver.find_element(By.ID, 'login-button').click()
        # get html page source
        get_source = self.driver.page_source

        self.assertIn('Invalid username or password', get_source)
