from random import randint

from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.staticfiles import finders
from django.test import LiveServerTestCase, Client
from django.utils import timezone
from lxml import html

from CoolSchool import settings
from articles_app.admin import admin_site
from .models import Page, Article


class ArticlesAppTests(LiveServerTestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username='admin',
            password='password',
            email='admin@example.com'
        )
        self.client = Client()
        self.admin_url = self.live_server_url + '/admin/'
        self.default_pages = settings.DEFAULT_PAGES
        for title in self.default_pages.keys():
            Page.objects.get_or_create(title=title, page_url=self.default_pages[title]['url'],
                                       edit_url=self.default_pages[title]['edit_url'])

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

    def test_admin_logout(self):
        logged_in = self.client.login(username='admin', password='password')
        self.assertTrue(logged_in, "User not logged in correctly")
        self.assertTrue(auth.get_user(self.client).is_authenticated)
        admin_page_response = self.client.get(self.admin_url)
        admin_site_tree = html.fromstring(admin_page_response.content)
        self.assertEqual(admin_site_tree.get_element_by_id("admin_title").text, 'Strona Admina Cool School')
        self.client.get('/logout/')
        self.assertFalse(auth.get_user(self.client).is_authenticated)

    def test_default_pages_urls(self):
        default_urls = [page['url'] for _, page in settings.DEFAULT_PAGES.items()]
        for url in default_urls:
            url = url.split('/')[0]
            response = self.client.get(f'/{url}/')
            status_code = response.status_code
            self.assertTrue(status_code != 404, f'Page {url} is returning {status_code}')

    def test_articles_loaded_from_db(self):
        for page_title, urls in self.default_pages.items():
            page = Page.objects.get_or_create(title=page_title)[0]
            Article.objects.get_or_create(title='Test Title', content='Test Content', pub_date=timezone.now(),
                                          page=page)
            response = self.client.get(f"/{urls['url']}")
            site_tree = html.fromstring(response.content)
            article_title = site_tree.xpath("//article/h1")[0].text
            self.assertEqual(article_title, 'Test Title')

    # TODO
    def test_edit_pages_urls(self):
        pass

    # TODO CI/CD on github research
    # TODO CSS for admin page
    # TODO CSS for articles
    # TODO Docker research

    # TODO
    def test_all_links_returns_200(self):
        pass

    # TODO
    def test_edit_forms(self):
        pass

    def test_edition_of_articles(self):
        pass

    def test_previously_added_articles_shown_on_edit_pages(self):
        pass





