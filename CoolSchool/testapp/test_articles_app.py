from django.test import LiveServerTestCase, Client
from selenium import webdriver


class ArticlesTestCase(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Safari()

    def tearDown(self):
        self.browser.quit()

    def test_selenium_starts(self):
        self.browser.get(self.live_server_url)

    def test_index_template_render(self):
        client = Client()
        response = client.get(self.live_server_url)
        self.assertTemplateUsed(response, 'articles_app/index.html')
