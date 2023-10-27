from django.test import LiveServerTestCase, Client
from articles_app.admin import admin_site
from django.contrib.staticfiles import finders
from .models import Page, Article
from django.contrib.auth.models import User
from lxml import html
from random import randint
from CoolSchool import settings


class ArticlesAppTests(LiveServerTestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username='admin',
            password='password',
            email='admin@example.com'
        )
        self.client = Client()
        self.admin_url = self.live_server_url + '/admin/'

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

    def test_name_of_pages_are_loaded_from_database(self):
        logged_in = self.client.login(username='admin', password='password')
        self.assertTrue(logged_in, "User not logged in correctly")
        pages = []
        titles = settings.DEFAULT_PAGES.keys()
        for title in titles:
            url = settings.DEFAULT_PAGES[title]['url']
            edit_url = settings.DEFAULT_PAGES[title]['edit_url']
            pages.append(Page.objects.get_or_create(title=title, page_url=url,
                                                    edit_url=edit_url)[0])
            self.assertIsNotNone(Page.objects.get(title=title))
            self.assertEqual(pages[-1].title, title)
            self.assertEqual(pages[-1].page_url, url)
            self.assertEqual(pages[-1].edit_url, edit_url)

        response = self.client.get(self.admin_url)
        if response.status_code == 200:
            admin_site_tree = html.fromstring(response.content)
            add_links = admin_site_tree.xpath("//a[@class='addlink']")
            for link, page in zip(add_links, pages):
                self.assertEqual(link.attrib['href'], page.edit_url)
                self.assertEqual(link.text, page.title)
        else:
            raise AssertionError(f'Cannot get admin page. Status code {response.status_code}')

        rng = randint(0, len(pages) - 1)
        random_page = pages[rng]
        random_page.title = 'NEW_TITLE'
        random_page.save()

        response = self.client.get(self.admin_url)
        if response.status_code == 200:
            admin_site_tree = html.fromstring(response.content)
            add_links = admin_site_tree.xpath("//a[@class='addlink']")
            link = add_links[rng]
            self.assertEqual(link.attrib['href'], random_page.edit_url)
            self.assertEqual(link.text, random_page.title)
        else:
            raise AssertionError(f'Cannot get admin page after modification. Status code {response.status_code}')

    # TODO
    def test_admin_logout(self):
        logged_in = self.client.login(username='admin', password='password')
        self.assertTrue(logged_in, "User not logged in correctly")
        response = self.client.get('/admin/')
