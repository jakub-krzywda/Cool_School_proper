from django.test import LiveServerTestCase, Client
from articles_app.admin import admin_site
from django.contrib.staticfiles import finders
from .models import Page, Article
from django.contrib.auth.models import User


class ArticlesAppTests(LiveServerTestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username='admin',
            password='password',
            email='admin@example.com'
        )
        self.client = Client()

    def tearDown(self) -> None:
        pass

    def test_index_template_render(self):
        response = self.client.get(self.live_server_url)
        self.assertTemplateUsed(response, 'index.html')

    def test_static_files_available(self):
        static_files = [
            'css/styles.css',
            'img/logo2.png',
            'favicon.ico'
        ]

        for static_file in static_files:
            result = finders.find(static_file)
            self.assertIsNotNone(result, f'Plik statyczny {static_file} nie istnieje.')

    def test_models_registered_correctly(self):
        self.assertIn(Page, admin_site._registry)
        self.assertIn(Article, admin_site._registry)

    def test_admin_template_render_with_login(self):
        logged_in = self.client.login(username='admin', password='password')
        self.assertTrue(logged_in, "User not logged in correctly")
        response = self.client.get('/admin/')
        self.assertTemplateUsed(response, 'admin/admin.html')

    # TODO
    def test_name_of_pages_are_loaded_from_variables(self):
        pass
