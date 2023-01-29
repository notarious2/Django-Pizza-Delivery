from store.models import Product
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile


class TestProductAppearance(StaticLiveServerTestCase):
    """Test Product with no Image appears"""

    def setUp(self):
        chromedriver_autoinstaller.install()
        options = webdriver.ChromeOptions()
        # to run without openning browser
        options.add_argument('headless')
        # to ignore errors in terminal
        options.add_experimental_option(
            'excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=options)

        self.products_url = self.live_server_url + reverse('store:products')

    def tearDown(self):
        self.driver.close()

    def test_single_product_is_appearing(self):
        """Test that single product without image is appearing"""
        Product.objects.create(name='Test Product')

        self.driver.get(self.products_url)
        product = self.driver.find_element(
            By.CLASS_NAME, 'individual-container')
        title = product.find_element(By.CSS_SELECTOR, 'h5')
        self.assertEqual(title.text, 'Test Product')

    def test_multiple_products_are_appearing(self):
        """Test that multiple products are appearing"""
        test_products = ['test product 1', 'test product 2', 'test product 3']
        for product in test_products:
            Product.objects.create(name=product)

        self.driver.get(self.products_url)

        products = self.driver.find_elements(
            By.CLASS_NAME, 'individual-container')

        self.assertEqual(len(products), len(test_products))

        for product, test_product in zip(products, test_products):
            product_title = product.find_element(By.CSS_SELECTOR, 'h5').text
            self.assertEqual(product_title, test_product)


class TestProductAppearanceWithImage(StaticLiveServerTestCase):
    """Test Product with Image appears"""

    def setUp(self):
        chromedriver_autoinstaller.install()
        options = webdriver.ChromeOptions()
        # to run without openning browser
        options.add_argument('headless')
        # to ignore errors in terminal
        options.add_experimental_option(
            'excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=options)

        self.products_url = self.live_server_url + reverse('store:products')

        with open("functional_tests/test_image.jpg", "rb") as image:
            self.image = SimpleUploadedFile(
                "test_image.jpg", image.read(), content_type="image/jpg")

    def tearDown(self):
        self.driver.close()

    def test_single_product_with_image_appears(self):
        """Test that single product with image is appearing"""

        product = Product.objects.create(name='Test Product', image=self.image)

        self.driver.get(self.products_url)

        found_product = self.driver.find_element(
            By.CLASS_NAME, 'individual-container')

        image = found_product.find_element(By.CSS_SELECTOR, 'img')
        assert image
        product.image.delete()
