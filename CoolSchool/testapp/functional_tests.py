from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from selenium import webdriver
import time

from selenium.webdriver.common.by import By


class FunctionalTests(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.url_admin = self.live_server_url + '/admin'

    def tearDown(self):
        self.browser.quit()

    def login_admin(self, login, password):
        self.browser.get(self.url_admin)
        self.browser.maximize_window()
        username_input = self.browser.find_element(By.ID, 'id_username')
        password_input = self.browser.find_element(By.ID, 'id_password')
        login_button = self.browser.find_element(By.XPATH, "//input[@type='submit']")
        username_input.click()
        time.sleep(1)
        username_input.send_keys(login)
        time.sleep(1)
        password_input.click()
        time.sleep(1)
        password_input.send_keys(password)
        time.sleep(1)
        login_button.click()
        time.sleep(1)

    def test_selenium_starts(self):
        self.browser.get(self.live_server_url)
        time.sleep(5)

    def test_user_comes_to_site_and_checks_navigation_bar_and_title(self):
        """
        1. User comes to site typing in live server's url
        2. User maximizes window
        3. User checks if sites title is CoolSchool
        4. User checks if navigation bar on top is present
        5. User checks if logo is present
        6. User closes browser
        """
        self.browser.get(self.live_server_url)
        self.browser.maximize_window()
        self.assertIn('Cool School', self.browser.title)
        navbar_nav = self.browser.find_element(By.ID, "navbarNav")
        self.assertEqual(navbar_nav.text, 'Aktualności\nKursy\nRegulamin\nKontakt\nPolityka Prywatności')
        logo = self.browser.find_element(By.ID, "imgLogo")
        self.assertEqual(logo.size['height'], 69)
        self.assertEqual(logo.size['width'], 323)

    def test_user_comes_to_site_and_checks_favicon(self):
        """
        1. User comes to site typing in live server's url
        2. User maximizes window
        3. User checks if site has icon in tab menu
        """
        self.browser.get(self.live_server_url)
        self.browser.maximize_window()
        favicon = self.browser.find_element(By.XPATH, "//*[@rel='icon']")
        self.assertIsNotNone(favicon)

    def test_user_comes_to_admin_site_positive(self):
        """
        1. User comes to <live_server_url>/admin
        2. Login panel is present
        3. User enters right login and password
        4. User sees admin site
        5. User leaves the page
        """
        # store the password to login later
        login = "testUser"
        password = "testPassword"
        User.objects.create_superuser(login, 'myemail@test.com', password)
        self.login_admin(login, password)
        header = self.browser.find_element(By.XPATH, "//a[@href='/admin/']")
        self.assertEqual(header.text, "Cool School Admin Page")

    def test_user_comes_to_admin_site_negative(self):
        """
        1. User comes to <live_server_url>/admin
        2. Login panel is present
        3. User enters wrong login and password
        4. User sees error message
        5. User leaves the page
        """
        login = "testUser"
        password = "testPassword"
        User.objects.create_superuser(login, 'myemail@test.com', password)
        self.login_admin(login, 'wrong_pass')
        error = self.browser.find_element(By.CSS_SELECTOR, "p.errornote")
        self.assertIn("Please enter the correct username and password", error.text)

