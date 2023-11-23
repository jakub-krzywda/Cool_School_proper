import random

from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from selenium import webdriver
from CoolSchool.settings import DEFAULT_PAGES
import time
from selenium.webdriver.common.by import By
from articles_app.models import Page
from CoolSchool import settings


def wait_after_fail(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            if hasattr(e, 'msg'):
                input(f'\033[31mTest failed.\n {e.msg}\033[0m\n Press any key to exit')
                LiveServerTestCase.fail(e)
            elif hasattr(e, 'args'):
                input(f'\033[31mTest failed.\n {e.args[0]}\033[0m\n Press any key to exit')
                LiveServerTestCase.fail(e)
            else:
                LiveServerTestCase.fail(e)

    return wrapper


class FunctionalTests(LiveServerTestCase):

    def setUp(self):
        self.url_admin = self.live_server_url + '/admin'
        self.sleep_time = 0.1
        self.browser = webdriver.Firefox()
        default_pages = settings.DEFAULT_PAGES
        for title in default_pages.keys():
            Page.objects.get_or_create(title=title, page_url=default_pages[title]['url'],
                                       edit_url=default_pages[title]['edit_url'])

    def tearDown(self):
        self.browser.quit()

    def login_admin(self, login, password):
        self.browser.get(self.url_admin)
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
        expected_links = tuple(settings.DEFAULT_PAGES.keys())
        actual_links = navbar_nav.text.split('\n')
        for link in actual_links:
            self.assertIn(link, expected_links)
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
        header = self.browser.find_element(By.ID, 'admin_title')
        self.assertEqual(header.text, "Strona Admina Cool School")

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
        self.assertIn("Wprowadź poprawne dane w polach ", error.text)

    # @wait_after_fail
    def test_adding_article(self):
        # 1. User comes to <live_server_url>/admin
        # 2. Login panel is present
        # 3. User enters right login and password
        login = "testUser"
        password = "testPassword"
        User.objects.create_superuser(login, 'myemail@test.com', password)
        self.login_admin(login, password)

        # 4. User sees admin page
        # 5. Main header says "Strona Admina Cool School"
        header = self.browser.find_element(By.ID, "admin_title")
        self.assertEqual("Strona Admina Cool School", header.text)

        # 6. Under main header there is a menu that says "Witaj <name of the user>." And has options such as:
        # [Zobacz stronę, Zmień hasło, Wyloguj]
        user_tools = self.browser.find_element(By.CSS_SELECTOR, 'p.admin_welcome')
        self.assertIn(f'Witaj, {login}', user_tools.text)
        user_tools_links = self.browser.find_elements(By.CSS_SELECTOR, "a.nav-link.admin_welcome")
        expected_tools_a = ('Zobacz stronę', 'Zmień hasło', 'Wyloguj')
        found_links = [item.accessible_name for item in user_tools_links]
        for a in expected_tools_a:
            self.assertIn(a, found_links)

        # 7. Subheader says "Poniżej wybierz stronę na którą chcesz dodać artykuł i kliknij dodaj"
        subheader = self.browser.find_element(By.XPATH, "//div[@id='content']//h2")
        self.assertEqual("Poniżej wybierz stronę na którą chcesz dodać artykuł", subheader.text)

        # 8. Caption says "Strony"
        caption = self.browser.find_element(By.ID, 'pages_caption')
        self.assertEqual(caption.text, 'Strony')

        # 9. Below there is a list containing pages that can be modified: [Główna, Aktualności, Kursy, Regulamin,
        #                                                                 Polityka_Prywatności]
        pages = self.browser.find_elements(By.XPATH, "//ul/li[@class=page_name]")
        page_names = [a.text for a in pages]
        expected_names = tuple(settings.DEFAULT_PAGES.keys())
        for name in page_names:
            self.assertIn(name, expected_names)

        # 10. In each page's row there is "Dodaj" (add) button
        add_links = self.browser.find_elements(By.XPATH, "//ul/li[@class='page_name']//a[@class='addlink']")
        add_links_names = [a.text for a in add_links]
        for add_link in add_links_names:
            self.assertIn(add_link, expected_names)

        random_page = random.choice(add_links)
        random_page_name = random_page.accessible_name
        random_page.click()
        time.sleep(self.sleep_time)

        # 11. After clicking "Dodaj" User is presented with edit page, which has title of edited page (Główna, Aktualności, Kursy etc.)
        edit_page_title = self.browser.find_element(By.ID, "edit_page_title")
        self.assertEqual(edit_page_title.text, random_page_name)

        # 11.1 There is a form where (s)he can add new article with such parameters as:
        #     [Tytuł(title), Zawartość(content)] and buttons "Zapisz"(save), "Zapisz i dodaj kolejny"(save and add next),
        #     "Zapisz i kontynuuj edycje" (save and continue editing)
        title_label = self.browser.find_element(By.XPATH, "//label[@for='id_title']").text
        content_label = self.browser.find_element(By.XPATH, "//label[@for='id_content']").text
        self.assertEqual('Tytuł', title_label)
        self.assertEqual('Zawartość', content_label)

        # 12. User enters title and content and clicks save
        title_form = self.browser.find_element(By.ID, 'id_title')
        content_form = self.browser.find_element(By.ID, 'id_content')
        title_form.click()
        time.sleep(self.sleep_time)
        title_form.send_keys('Title')
        time.sleep(self.sleep_time)
        content_form.click()
        time.sleep(self.sleep_time)
        content_form.send_keys('Content')
        time.sleep(self.sleep_time)
        save_buttons = self.browser.find_elements(By.XPATH, "//button[@type='submit']")
        save_buttons_values = [button.accessible_name for button in save_buttons]
        expected_button_names = ("Zapisz", "Zapisz i dodaj kolejny",
                                 "Zapisz i kontynuuj edycje")
        self.assertTrue(all([button_value in expected_button_names for button_value in save_buttons_values]),
                        'Wrong button names')
        save_buttons[0].click()

        time.sleep(self.sleep_time)

    def test_logged_user_clicks_on_show_page(self):
        # 1. User comes to admin page using admin url
        # 2. User is presented with a login page
        # 3. User enters login and password and clicks enter
        sleep_time = 0.1
        login = "testUser"
        password = "testPassword"
        User.objects.create_superuser(login, 'myemail@test.com', password)
        self.login_admin(login, password)
        # 4. User is presented with admin page
        header = self.browser.find_element(By.ID, "admin_title")
        self.assertEqual("Strona Admina Cool School", header.text)
        admin_tools = self.browser.find_elements(By.XPATH, "//a[@class='nav-link admin_welcome']")

        # 5. User clicks on "View site" button
        view_link = [el for el in admin_tools if el.text == 'Zobacz stronę'][0]
        view_link.click()
        time.sleep(sleep_time)
        # 6. User is presented with a main page
        navbar_nav = self.browser.find_element(By.ID, "navbarNav")
        for page_name in settings.DEFAULT_PAGES.keys():
            if page_name != 'Główna':
                self.assertIn(page_name, navbar_nav.text.split('\n'))
        logo = self.browser.find_element(By.ID, "imgLogo")
        self.assertEqual(logo.size['height'], 69)
        self.assertEqual(logo.size['width'], 323)
        # 7. User closes browser
        time.sleep(2)

    def test_admin_logout(self):
        # 1. User comes to admin page using admin url
        # 2. User is presented with a login page
        # 3. User enters login and password
        login = "testUser"
        password = "testPassword"
        User.objects.create_superuser(login, 'myemail@test.com', password)
        self.login_admin(login, password)
        # 4. User is presented with admin page
        header = self.browser.find_element(By.ID, "admin_title")
        self.assertEqual("Strona Admina Cool School", header.text)
        admin_tools = self.browser.find_elements(By.XPATH, "//a[@class='nav-link admin_welcome']")
        # 5. User clicks logout button in navbar
        logout_button = [_ for _ in admin_tools if _.text == 'Wyloguj'][0]
        logout_button.click()
        time.sleep(self.sleep_time)
        # 6. Site comes to log-out screen
        login_site_name = self.browser.find_element(By.XPATH, "//div[@id='content']//h1")
        self.assertEqual(login_site_name.text, 'Wylogowany(-na)')
        # 7. User closes browser

    def test_edit_page_available_only_for_logged_in_superuser(self):
        # 1. User is not logged in
        # 2. User comes to one of the edit urls straight
        edit_urls = [v['edit_url'] for k, v in DEFAULT_PAGES.items()]
        for url in edit_urls:
            self.browser.get(self.live_server_url + url)
            time.sleep(2)
            header = self.browser.find_element(By.XPATH, "//h1")
            self.assertNotIn(header.text, list(DEFAULT_PAGES.keys()))
            # 3. User is presented with the error screen
            self.assertEqual(self.browser.title, "Not Found")

        # 4. User closes browser

    def test_clicking_on_navbar_items_redirects_to_pages(self):
        # 1. User enters live servers url
        self.browser.get(self.live_server_url)
        # 2. User is presented with main page
        self.assertIn('Cool School', self.browser.title)
        navbar_nav = self.browser.find_element(By.ID, "navbarNav")
        # 3. For every link in navbar
        #   * User clicks on link
        #   * User is redirected to page corresponding to that link
        #   * User verifies if right page is displayed
        nav_links = self.browser.find_elements(By.XPATH, "//a[@class='nav-link']")
        for i in range(len(nav_links)):
            nav_links = self.browser.find_elements(By.XPATH, "//a[@class='nav-link']")
            link = nav_links[i]
            link_text = link.text
            link.click()
            self.browser.implicitly_wait(2)
            self.assertEqual(self.browser.current_url, f"{self.live_server_url}/{DEFAULT_PAGES[link_text]['url']}")
            self.browser.back()
        # 4. User closes browser

    def test_added_new_articles_appears_on_proper_pages(self):
        # 1. User comes to <live_server_url>/admin
        # 2. Login panel is present
        # 3. User enters right login and password
        # 4. For every link redirecting to edit pages:
        #   * Click on the link
        #   * Page with Title, existing articles with edit and delete buttons, Add new article button and Title is presented
        #   * User clicks on "Add new article" button
        #   * Form with Title, content and save button is presented
        #   * Content can be edited as in text editor
        #   * User clicks on Save button
        #   * "Do you want to save this article" prompt is presented with options "yes" and "no"
        #   * User clicks on "yes"
        #   * User goes back to previous page were he can choose which site to edit
        # 5. User clicks on "Show page" button on top of the edit page
        # 6. For every link in navigation menu:
        #   * Click on navigation menu link
        #   * User is presented with corresponding page
        #   * User checks if previously added article is presented on the page in proper place
        pass
