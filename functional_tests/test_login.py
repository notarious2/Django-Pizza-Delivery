from selenium import webdriver
from users.models import Customer
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import LiveServerTestCase
from django.urls import reverse
import chromedriver_autoinstaller
import time
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from users.models import Customer
from django.contrib.auth.models import User


class TestCustomerLogin(StaticLiveServerTestCase):

    def setUp(self):
        chromedriver_autoinstaller.install()
        options = webdriver.ChromeOptions()
        options.add_experimental_option(
            'excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=options)

        self.credentials = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        User.objects.create_user(**self.credentials)

    def tearDown(self):
        self.driver.close()

    def test_login_with_valid_credentials(self):
        """Test user logs in with valid credentials"""
        login_url = self.live_server_url + reverse('users:login')
        expected_url = self.live_server_url + reverse('store:products')

        self.driver.get(login_url)

        username = self.driver.find_element(By.NAME, 'username')
        password = self.driver.find_element(By.NAME, 'password')
        button_selector = 'body > div > form > button'
        username.send_keys('testuser')
        password.send_keys('testpassword')
        self.driver.find_element(By.CSS_SELECTOR, button_selector).click()
        self.assertEqual(self.driver.current_url, expected_url)

    def test_login_with_invalid_credentials(self):
        """Test log in attempt with invalid credentials"""
        login_url = self.live_server_url + reverse('users:login')

        self.driver.get(login_url)
        username = self.driver.find_element(By.NAME, 'username')
        password = self.driver.find_element(By.NAME, 'password')
        button_selector = 'body > div > form > button'
        username.send_keys('testuser')
        password.send_keys('wrongpassword')
        self.driver.find_element(By.CSS_SELECTOR, button_selector).click()
        get_source = self.driver.page_source

        self.assertIn('Invalid username or password', get_source)
        time.sleep(10)


# class TestLogin(LiveServerTestCase):
#     def setUp(self):
#         chromedriver_autoinstaller.install()
#         self.browser = webdriver.Chrome()

#     def test_login(self):
#         self.browser.get('http://127.0.0.1:8000')
#         time.sleep(10)
