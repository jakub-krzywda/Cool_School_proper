import unittest

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

    @unittest.expectedFailure
    def test_adding_article(self):
        """
        1. User comes to <live_server_url>/admin
        2. Login panel is present
        3. User enters right login and password
        4. User sees admin page
        5. Main header says "Strona Admina Cool School"
        6. Under main header there is a menu that says "Witaj <name of the user>." And has options such as:
        [Zobacz stronę, Zmień hasło, Wyloguj]
        7. Subheader says "Poniżej wybierz stronę na którą chcesz dodać artykuł i kliknij dodaj"
        8. Caption says "Strony"
        9. Below there is a list containing pages that can be modified: [Główna, Aktualności, Kursy, Regulamin,
                                                                        Polityka_Prywatności]
        10. In each page's row there are "Dodaj" (add) and "Edytuj" (edit) buttons
        11. After clicking "Dodaj" User is presented with Page where (s)he can add new article with such parameters as:
            [Tytuł(title), Zawartość(content)] and buttons "Zapisz"(save), "Zapisz i dodaj kolejny"(save and add next),
            "Zapisz i kontynuuj edycje" (save and continue editing)
        12. User enters title and content and clicks save
        13. User is presented with a list of arguments with Title as entered before
        14. User clicks on the article
        15. Same view is presented but with additional "usuń"(delete) button
        16. User clicks delete button
        17. User is presented with Confirmation screen with buttons "Tak, jestem pewny"(Yes, I'm sure) i
        "Nie, Wróć" (No, take me back)
        18. User clicks on "Tak, jestem pewny"
        19. User is back on Article list for selected site page
        20. User closes browser
        """
        login = "testUser"
        password = "testPassword"
        User.objects.create_superuser(login, 'myemail@test.com', password)
        self.login_admin(login, password)
        header = self.browser.find_element(By.XPATH, "//a[@href='/admin/']")
        self.assertEqual("Strona Admina Cool School", header.text)
        user_tools = self.browser.find_element(By.ID, 'user-tools')
        self.assertIn(f'Witaj, {login.upper()}', user_tools.text)
        user_tools_links = self.browser.find_elements(By.XPATH, "//*[@id='user-tools']/a")
        user_tools_buttons = self.browser.find_elements(By.XPATH,
                                                        "//*[@id='user-tools']/form[@id='logout-form']//button")
        expected_tools_a = ('Zobacz stronę', 'Zmień hasło')
        expected_buttons = 'Wyloguj'
        found_links = [item.accessible_name for item in user_tools_links]
        found_buttons = [item.accessible_name for item in user_tools_buttons]

        for a in expected_tools_a:
            self.assertIn(a, found_links)

        self.assertIn(expected_buttons, found_buttons)

        subheader = self.browser.find_element(By.XPATH, "//div[@id='content']//h1")
        self.assertEqual("Poniżej wybierz stronę na którą chcesz dodać artykuł i kliknij dodaj", subheader.text)

        caption = self.browser.find_element(By.XPATH, "//div[@class='app-articles_app module']//table//caption//a")
        self.assertEqual(caption.text, 'Strony')

        pages = self.browser.find_elements(By.XPATH, "//tbody//tr//th//a")
        page_names = [a.text for a in pages]
        expected_names = ('Główna', 'Aktualności', 'Kursy', 'Regulamin', 'Polityka_Prywatności')
        for name in page_names:
            self.assertIn(name, expected_names)

        add_links = self.browser.find_elements(By.XPATH,
                                               "//div[@class='app-articles_app module']//table//tbody//tr//td//a[@class='addlink']")

        add_links_names = [a.text for a in add_links]

        for add_link in add_links_names:
            self.assertEqual(add_link, 'Dodaj')

        change_links = self.browser.find_elements(By.XPATH,
                                                  "//div[@class='app-articles_app module']//table//tbody//tr//td//a[@class='changelink']")

        change_links_names = [a.text for a in change_links]

        for change_link in change_links_names:
            self.assertEqual(change_link, 'Edytuj')

        add_links[0].click()

        time.sleep(2)

        title_label = self.browser.find_element(By.XPATH, "//label[@for='id_title']").text
        content_label = self.browser.find_element(By.XPATH, "//label[@for='id_content']").text

        self.assertEqual('Tytuł', title_label)
        self.assertEqual('Zawartość', content_label)

        title_form = self.browser.find_element(By.ID, 'id_title')
        content_form = self.browser.find_element(By.ID, 'id_content')

        title_form.click()
        time.sleep(1)
        title_form.send_keys('Title')
        time.sleep(1)
        content_form.click()
        time.sleep(1)
        content_form.send_keys('Content')
        time.sleep(1)

        save_buttons = self.browser.find_elements(By.XPATH, "//input[@type='submit']")
        save_buttons_values = [button.accessible_name for button in save_buttons]

        expected_button_names = ("Zapisz", "Zapisz i dodaj kolejny",
                                 "Zapisz i kontynuuj edycje")
        for button_value in save_buttons_values:
            self.assertIn(button_value, expected_button_names)

        save_buttons[0].click()

        time.sleep(5)

        #TODO
        # 13. User is presented with a list of articles with Title as entered before
        # 14. User clicks on the article
        # 15. Same view is presented but with additional "usuń"(delete) button
        # 16. User clicks delete button
        # 17. User is presented with Confirmation screen with buttons "Tak, jestem pewny"(Yes, I'm sure) i
        # "Nie, Wróć" (No, take me back)
        # 18. User clicks on "Tak, jestem pewny"
        # 19. User is back on Article list for selected site page
        # 20. User closes browser
