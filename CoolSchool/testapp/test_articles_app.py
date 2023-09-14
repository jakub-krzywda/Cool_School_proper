from django.test import LiveServerTestCase
from selenium import webdriver


class ArticlesTestCase(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Safari()

    def tearDown(self):
        self.browser.quit()

    def test_selenium_starts(self):
        self.browser.get(self.live_server_url)
