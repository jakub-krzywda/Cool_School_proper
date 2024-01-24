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

        for page in Page.objects.all():
            Article.objects.get_or_create(title='Test Title1', content='Test Content', pub_date=timezone.now(),
                                          page=page, show_on_whiteboard=True)
            Article.objects.get_or_create(title='Test Title2', content='Test Content', pub_date=timezone.now(),
                                          page=page, show_on_whiteboard=False)

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

    def test_edit_pages_urls(self):
        default_edit_urls = [page['edit_url'] for _, page in settings.DEFAULT_PAGES.items()]
        self.client.login(username='admin', password='password')
        for url in default_edit_urls:
            response = self.client.get(f'{url}')
            self.assertEqual(response.status_code, 200, f"Url: {url} is not correct")

    def test_all_links_returns_200(self):
        response = self.client.get(self.live_server_url)
        site_tree = html.fromstring(response.content)
        links = site_tree.xpath("//a")
        for link in links:
            response = self.client.get(link.attrib['href'])
            self.assertEqual(response.status_code, 200, f"Url: {link.attrib['href']} is not correct")

    def test_edition_of_articles(self):
        self.client.login(username='admin', password='password')
        articles = Article.objects.all()
        article0 = articles[0]
        article_edit_url = f'{self.live_server_url}/edit_article/{article0.id}/'
        response = self.client.get(article_edit_url)
        self.assertEqual(response.status_code, 200, f"Url: {article_edit_url} is not correct")

    def test_previously_added_articles_shown_on_edit_pages(self):
        self.client.login(username='admin', password='password')
        pages = Page.objects.all()
        for page in pages:
            response = self.client.get(page.edit_url)
            site_tree = html.fromstring(response.content)
            articles = site_tree.xpath("//article")
            self.assertEqual(len(articles), 2)

    def test_adding_new_articles(self):
        self.client.login(username='admin', password='password')
        pages = Page.objects.all()
        for page in pages:
            response = self.client.post(page.edit_url, {'title': 'Test Title3', 'content': 'Test Content3'})
            self.assertEqual(response.status_code, 302, f"Url: {page.edit_url} is not correct")
            response = self.client.get(f'/{page.page_url}')
            site_tree = html.fromstring(response.content)
            article_title = site_tree.xpath("//article/h1")[0]
            self.assertIn('Test Title3', article_title.text)
            self.assertIn('Test Content3', response.content.decode('utf-8'))

    def test_article_deletion(self):
        self.client.login(username='admin', password='password')
        articles = Article.objects.all()
        article0 = articles[0]
        article_delete_url = f'{self.live_server_url}/delete_article/{article0.id}/'
        response = self.client.get(article_delete_url)
        self.assertEqual(response.status_code, 302, f"Url: {article_delete_url} is not correct")
        response = self.client.get(article0.page.page_url)
        site_tree = html.fromstring(response.content)
        articles = site_tree.xpath("//article")
        self.assertEqual(len(articles), 1)

    def test_show_on_whiteboard_option_present_in_news_edit_page(self):
        self.client.login(username='admin', password='password')
        response = self.client.get('/add_article/news/')
        site_tree = html.fromstring(response.content)
        show_on_whiteboard_checkbox = site_tree.xpath("//input[@id='show_on_whiteboard']")
        self.assertEqual(len(show_on_whiteboard_checkbox), 1)

    def test_show_on_whiteboard_option_not_present_on_edit_pages_other_than_news(self):
        self.client.login(username='admin', password='password')
        pages = Page.objects.all()
        pages = [page for page in pages if page.title != 'Aktualności']
        for page in pages:
            response = self.client.get(page.edit_url)
            site_tree = html.fromstring(response.content)
            show_on_whiteboard_checkbox = site_tree.xpath("//input[@id='show_on_whiteboard']")
            self.assertFalse(show_on_whiteboard_checkbox)

    def test_whiteboard_present_on_main_page(self):
        response = self.client.get('/')
        site_tree = html.fromstring(response.content)
        whiteboard = site_tree.xpath("//div[@id='whiteboard']")
        self.assertEqual(len(whiteboard), 1)

    def test_whiteboard_not_present_on_other_pages(self):
        pages = Page.objects.all()
        pages = [page for page in pages if page.title != 'Główna']
        for page in pages:
            response = self.client.get(f'/{page.page_url}')
            site_tree = html.fromstring(response.content)
            whiteboard = site_tree.xpath("//ul[@id='whiteboard']")
            self.assertFalse(whiteboard)

    def test_whiteboard_links_are_correct(self):
        response = self.client.get('/')
        site_tree = html.fromstring(response.content)
        whiteboard = site_tree.xpath("//div[@id='whiteboard']/div/div/ul/li/a")
        self.assertEqual(len(whiteboard), 1)
        self.assertTrue(whiteboard[0].attrib['href'].startswith('/news/#'))

    def test_articles_are_in_order_from_newest_to_oldest(self):
        pages = Page.objects.all()
        for page in pages:
            response = self.client.get(f'/{page.page_url}')
            site_tree = html.fromstring(response.content)
            articles = site_tree.xpath("//article/h1")
            articles = [article.text for article in articles]
            self.assertEqual(articles, ['Test Title2', 'Test Title1'], f'Articles are not in order on page {page.title}')
