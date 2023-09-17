from django.test import LiveServerTestCase
from selenium import webdriver
import time

from selenium.webdriver.common.by import By


class FunctionalTests(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_selenium_starts(self):
        self.browser.get(self.live_server_url)
        time.sleep(5)

    def test_user_comes_to_site_and_checks_title(self):
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
