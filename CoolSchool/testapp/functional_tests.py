import random
import time

from django.contrib.auth.models import User
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from CoolSchool import settings
from CoolSchool.settings import DEFAULT_PAGES
from articles_app.models import Page


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
        self.sleep_time = 10
        self.browser = webdriver.Firefox()
        self.actions = ActionChains(self.browser)
        self.wait = WebDriverWait(self.browser, self.sleep_time)
        self.login = "testUser"
        self.password = "testPassword"
        User.objects.create_superuser(self.login, 'myemail@test.com', self.password)
        default_pages = settings.DEFAULT_PAGES
        for title in default_pages.keys():
            Page.objects.get_or_create(title=title, page_url=default_pages[title]['url'],
                                       edit_url=default_pages[title]['edit_url'])

    def tearDown(self):
        self.browser.quit()

    def login_admin(self, login='testUser', password='testPassword'):
        self.browser.get(self.url_admin)
        username_input = self.wait.until(EC.presence_of_element_located((By.ID, "id_username")))
        password_input = self.wait.until(EC.presence_of_element_located((By.ID, 'id_password')))
        login_button = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='submit']")))
        username_input.click()
        username_input.send_keys(login)
        password_input.click()
        password_input.send_keys(password)
        login_button.click()

    def test_selenium_starts(self):
        self.browser.get(self.live_server_url)

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
        self.login_admin()
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
        self.login_admin(self.login, 'wrong_pass')
        error = self.browser.find_element(By.CSS_SELECTOR, "p.errornote")
        self.assertIn("Wprowadź poprawne dane w polach ", error.text)

    # @wait_after_fail
    def test_adding_article(self):
        # 1. User comes to <live_server_url>/admin
        # 2. Login panel is present
        # 3. User enters right login and password
        self.login_admin()

        # 4. User sees admin page
        # 5. Main header says "Strona Admina Cool School"
        header = self.browser.find_element(By.ID, "admin_title")
        self.assertEqual("Strona Admina Cool School", header.text)

        # 6. Under main header there is a menu that says "Witaj <name of the user>." And has options such as:
        # [Zobacz stronę, Zmień hasło, Wyloguj]
        user_tools = self.browser.find_element(By.CSS_SELECTOR, 'p.admin_welcome')
        self.assertIn(f'Witaj, {self.login}', user_tools.text)
        user_tools_links = self.browser.find_elements(By.CSS_SELECTOR, "a.nav-link.admin_welcome")
        expected_tools_a = ('Zobacz stronę', 'Wyloguj')
        found_links = [item.accessible_name for item in user_tools_links]
        for a in expected_tools_a:
            self.assertIn(a, found_links)

        # 7. Subheader says "Poniżej wybierz stronę, którą chcesz edytować"
        subheader = self.browser.find_element(By.XPATH, "//div[@id='content']//h2")
        self.assertEqual("Poniżej wybierz stronę, którą chcesz edytować", subheader.text)

        # 8. Caption says "Strony"
        caption = self.browser.find_element(By.ID, 'pages_caption')
        self.assertEqual(caption.text, 'Strony')

        # 9. Below there is a list containing pages that can be modified: [Główna, Aktualności, Kursy, Regulamin,
        #                                                                 Polityka_Prywatności]
        pages = self.browser.find_elements(By.XPATH, "//ul/li[@class='page_name']")
        page_names = [a.text for a in pages]
        expected_names = tuple(settings.DEFAULT_PAGES.keys())
        self.assertTrue(pages)
        for name in page_names:
            self.assertIn(name, expected_names)

        # 10. Every page has a link that's name is the same as page's name and redirects to edit page
        add_links = self.browser.find_elements(By.XPATH, "//ul/li[@class='page_name']//a[@class='addlink']")
        add_links_names = [a.text for a in add_links]
        for add_link in add_links_names:
            self.assertIn(add_link, expected_names)

        # 10.1 User clicks on random page link
        random_page = random.choice(add_links)
        random_page_name = random_page.accessible_name
        random_page.click()

        # 11. After clicking link User is presented with edit page, which has title of edited page (Główna, Aktualności, Kursy etc.)
        edit_page_title = self.wait.until(EC.presence_of_element_located((By.ID, "edit_page_title")))
        self.assertEqual(edit_page_title.text, random_page_name)

        # 11.1 There is a button that says "Dodaj nowy artykuł"
        add_new_article_button = self.wait.until(EC.presence_of_element_located((By.ID, 'add_new')))
        add_new_article_button.click()

        # 11.2 There is a form where (s)he can add new article with such parameters as:
        #     [Tytuł(title), Zawartość(content)] and buttons "Zapisz"(save), "Zapisz i dodaj kolejny"(save and add next),
        #     "Zapisz i kontynuuj edycje" (save and continue editing)
        title_label = self.browser.find_element(By.XPATH, "//label[@for='id_title']").text
        content_label = self.browser.find_element(By.XPATH, "//label[@for='id_content']").text
        self.assertEqual('Tytuł:', title_label)
        self.assertEqual('Treść:', content_label)

        # 12. User enters title and content and clicks save
        self.browser.maximize_window()
        title_form = self.wait.until(EC.presence_of_element_located((By.ID, 'id_title')))
        ckeditor_form = self.browser.find_element(By.ID, 'cke_id_content')
        content_form = self.browser.find_element(By.XPATH, "//html/body")
        title_form.click()
        title_form.send_keys('Title')
        ckeditor_form.click()
        content_form.send_keys('Content')
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//button[@type='submit']")))
        save_buttons = self.browser.find_elements(By.XPATH, "//button[@type='submit']")
        save_buttons_values = [button.accessible_name for button in save_buttons]
        expected_button_names = ("Zapisz")
        self.assertTrue(all([button_value in expected_button_names for button_value in save_buttons_values]),
                        'Wrong button names')
        save_buttons[0].click()
        # 13. New added article appears on the page
        self.assertIn('Title', self.browser.page_source)
        self.assertIn('Content', self.browser.page_source)
        # 14. User quits the browser
        self.browser.quit()

    def test_logged_user_clicks_on_show_page(self):
        # 1. User comes to admin page using admin url
        # 2. User is presented with a login page
        # 3. User enters login and password and clicks enter
        sleep_time = 0.1
        self.login_admin()
        # 4. User is presented with admin page
        header = self.browser.find_element(By.ID, "admin_title")
        self.assertEqual("Strona Admina Cool School", header.text)
        admin_tools = self.browser.find_elements(By.XPATH, "//a[@class='nav-link admin_welcome']")

        # 5. User clicks on "View site" button
        view_link = [el for el in admin_tools if el.text == 'Zobacz stronę'][0]
        view_link.click()
        # 6. User is presented with a main page
        navbar_nav = self.wait.until(EC.presence_of_element_located((By.ID, "navbarNav")))
        for page_name in settings.DEFAULT_PAGES.keys():
            if page_name != 'Główna':
                self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@class='nav-link']")))
                self.assertIn(page_name, navbar_nav.text.split('\n'))
        logo = self.browser.find_element(By.ID, "imgLogo")
        self.assertEqual(logo.size['height'], 69)
        self.assertEqual(logo.size['width'], 323)
        # 7. User closes browser

    def test_admin_logout(self):
        # 1. User comes to admin page using admin url
        # 2. User is presented with a login page
        # 3. User enters login and password
        self.login_admin()
        # 4. User is presented with admin page
        header = self.browser.find_element(By.ID, "admin_title")
        self.assertEqual("Strona Admina Cool School", header.text)
        admin_tools = self.browser.find_elements(By.XPATH, "//a[@class='nav-link admin_welcome']")
        # 5. User clicks logout button in navbar
        logout_button = [_ for _ in admin_tools if _.text == 'Wyloguj'][0]
        logout_button.click()
        # 6. Site comes to log-out screen
        login_site_name = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='content']//h1")))
        self.assertEqual(login_site_name.text, 'Wylogowany(-na)')
        # 7. User closes browser

    def test_edit_page_available_only_for_logged_in_superuser(self):
        # 1. User is not logged in
        # 2. User comes to one of the edit urls straight
        edit_urls = [v['edit_url'] for k, v in DEFAULT_PAGES.items()]
        for url in edit_urls:
            self.browser.get(self.live_server_url + url)
            header = self.wait.until(EC.presence_of_element_located((By.XPATH, "//h1")))
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
        nav_link_texts = [link.text for link in nav_links]
        for i in range(len(nav_links)):
            nav_links = self.browser.find_elements(By.XPATH, "//a[@class='nav-link']")
            link = nav_links[i]
            link_text = nav_link_texts[i]
            link.click()
            self.browser.implicitly_wait(2)
            self.assertEqual(self.browser.current_url, f"{self.live_server_url}/{DEFAULT_PAGES[link_text]['url']}", f"Wrong url for page {link_text}")
            self.browser.back()
        # 4. User closes browser

    def test_added_new_articles_appears_on_proper_pages(self):
        # 1. User comes to <live_server_url>/admin
        # 2. Login panel is present
        # 3. User enters right login and password
        self.login_admin()
        # 4. For every link redirecting to edit pages:
        edit_links = self.browser.find_elements(By.XPATH, "//ul/li[@class='page_name']/a")
        for i in range(len(edit_links)):
            #   * Click on the link
            edit_links = self.browser.find_elements(By.XPATH, "//ul/li[@class='page_name']/a")
            link = edit_links[i]
            link.click()
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//button")))
            buttons = self.browser.find_elements(By.TAG_NAME, "button")
            buttons_texts = [button.text for button in buttons]
            #   * Page with Add new article button and Title is presented
            self.assertTrue('Dodaj nowy artykuł' in buttons_texts, 'There is no "Add new article" button')
            add_new_article_button = self.wait.until(EC.presence_of_element_located((By.ID, 'add_new')))
            #   * User clicks on "Add new article" button
            add_new_article_button.click()
            #   * Form with Title, content and save button is presented
            title_form = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='title']")))
            content_form = self.wait.until(EC.presence_of_element_located((By.XPATH, "/html/body")))

            self.assertTrue(title_form, 'There is no title input')
            self.assertTrue(content_form, 'There is no content input')
            save_button = self.wait.until(EC.element_to_be_clickable((By.ID, "save_button")))
            self.assertTrue('Zapisz' in save_button.text, 'There is no "Save" button')
            #   * Content can be edited as in text editor
            ckeditor_form = self.browser.find_element(By.ID, 'cke_id_content')
            content_form = self.browser.find_element(By.XPATH, "//html/body")
            self.assertTrue(ckeditor_form)
            title_form.click()
            title_form.send_keys('Test Title')
            ckeditor_form.click()
            content_form.send_keys('Test Content')
            #   * User clicks on Save button
            save_button = self.browser.find_element(By.ID, "save_button")
            self.wait.until(EC.visibility_of_element_located((By.ID, "save_button")))
            self.browser.maximize_window()
            save_button.click()
            self.browser.set_window_size(1920, 1080)
            #   * User goes back to previous page were he can choose which site to edit
            self.browser.back()
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//a[@class='nav-link admin_welcome']")))
            admin_tools = self.browser.find_elements(By.XPATH, "//a[@class='nav-link admin_welcome']")
        # 5. User clicks on "Show page" button on top of the edit page
        view_link = [el for el in admin_tools if el.text == 'Zobacz stronę'][0]
        view_link.click()
        # 6. For every link in navigation menu:
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='navbarNav']/ul/li/a")))
        navigation_menu_links = self.browser.find_elements(By.XPATH, "//div[@id='navbarNav']/ul/li/a")

        for i in range(len(navigation_menu_links)):
            #   * Click on navigation menu link
            navigation_menu_links = self.browser.find_elements(By.XPATH, "//div[@id='navbarNav']/ul/li/a")
            nav_link = navigation_menu_links[i]
            nav_link.click()
            #   * User is presented with corresponding page
            #   * User checks if previously added article is presented on the page in proper place
            self.assertTrue('Test Title' in self.browser.page_source)
            #   * User checks if articles title and content is presented
            self.assertTrue('Test Content' in self.browser.page_source)

    def test_contact_page_editing(self):
        # Fixture:
        # 1. User logs into admin panel
        self.login_admin()
        # Actual test:
        # 1. User goes to the admin panel
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//ul/li[@class='page_name']/a")))
        edit_links = self.browser.find_elements(By.XPATH, "//ul/li[@class='page_name']/a")
        # 2. User clicks on link to contact edit page
        contact_edit_link = [edit_link for edit_link in edit_links if edit_link.text == 'Kontakt'][0]
        contact_edit_link.click()

        # 3. User is presented with the contact site's edit page with "Find us on the map" section on the bottom
        header = self.wait.until(EC.presence_of_element_located((By.ID, "map")))
        self.assertEqual('Znajdź nas na mapie!', header.text)
        # 4. User clicks on "Add new article" button
        add_new_article_button = self.wait.until(EC.presence_of_element_located((By.ID, 'add_new')))
        add_new_article_button.click()
        # 5. User is presented with the adding article form
        # 6. User enters title and content
        # 7. User clicks on the save button
        title_field = self.browser.find_element(By.ID, "id_title")
        title_field.send_keys("Test title")
        ckeditor_form = self.browser.find_element(By.ID, "cke_id_content")
        content_form = self.browser.find_element(By.XPATH, "/html/body")
        ckeditor_form.click()
        content_form.send_keys('Test content')
        save_button = self.wait.until(EC.presence_of_element_located((By.XPATH, "//button[@type='submit']")))
        self.browser.maximize_window()
        save_button.click()
        # 10. User is redirected to Contact page with added article and "Find us on the map" section on the bottom
        header = self.wait.until(EC.presence_of_element_located((By.ID, "map")))
        self.assertEqual('Znajdź nas na mapie!', header.text)
        # 11. Previously added article's title and content is presented on the page
        self.assertTrue('Test title' in self.browser.page_source)
        self.assertTrue('Test content' in self.browser.page_source)

    def test_formatting_in_ckeditor(self):
        # Fixture:
        # 1. User logs into admin panel
        self.login_admin()
        # Actual test:
        # 1. User clicks on random page edit link
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//ul/li[@class='page_name']/a")))
        edit_links = self.browser.find_elements(By.XPATH, "//ul/li[@class='page_name']/a")
        random_edit_link = random.choice(edit_links)
        edit_link_url = random_edit_link.get_attribute("href")
        random_edit_link.click()
        # 2. User clicks on "Add new article" button
        add_new_article_button = self.wait.until(EC.presence_of_element_located((By.ID, 'add_new')))
        add_new_article_button.click()
        # 3. User is presented with add article interface (ckeditor)
        self.wait.until(EC.presence_of_element_located((By.ID, 'cke_id_content')))
        ckeditor = self.browser.find_element(By.ID, 'cke_id_content')
        self.assertTrue(ckeditor)
        # 4. User enters title
        title_field = self.browser.find_element(By.ID, "id_title")
        title_field.send_keys("Test title")
        # 5. User clicks on bold button
        bold_button = self.browser.find_element(By.CSS_SELECTOR, "span.cke_button__bold_icon")
        bold_button.click()
        # 6. User types in word "Bold"
        ckeditor_form = self.browser.find_element(By.XPATH, "/html/body")
        ckeditor_form.send_keys('Bold ')
        # 7. User clicks on table addition button
        table_addition_button = self.browser.find_element(By.CSS_SELECTOR, ".cke_button__table_icon")
        table_addition_button.click()
        # 8. User enters table parameters (number of rows and columns)
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "cke_dialog_title")))
        required_field_labels = self.browser.find_elements(By.CLASS_NAME, 'cke_required')
        row_number_field_id = [field for field in required_field_labels if field.accessible_name == "Liczba wierszy"][0].get_attribute("for")
        col_number_field_id = [field for field in required_field_labels if field.accessible_name == "Liczba kolumn"][0].get_attribute("for")
        row_number_field = self.browser.find_element(By.ID, row_number_field_id)
        row_number_field.click()
        row_number_field.clear()
        row_number_field.send_keys('3')
        col_number_field = self.browser.find_element(By.ID, col_number_field_id)
        col_number_field.click()
        col_number_field.clear()
        col_number_field.send_keys('6')
        # 8.1 User clicks on "OK" button
        cke_dialog_buttons = self.browser.find_elements(By.CLASS_NAME, "cke_dialog_ui_button")
        ok_button = [button for button in cke_dialog_buttons if button.accessible_name == "OK"][0]
        ok_button.click()
        # 9. User enters some content in table
        ckeditor_iframe = self.browser.find_element(By.CSS_SELECTOR, ".cke_wysiwyg_frame")
        self.browser.switch_to.frame(ckeditor_iframe)
        self.browser.maximize_window()
        table = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        self.assertTrue(table, "No table found")
        rows = table.find_elements(By.TAG_NAME, "tr")
        for i, row in enumerate(rows):
            cells = row.find_elements(By.TAG_NAME, "td")
            for j, cell in enumerate(cells):
                cell.click()
                self.actions.send_keys(f'row {i}, cell {j}')
                self.actions.perform()
        self.browser.switch_to.default_content()
        # 10. User saves an article
        save_button = self.wait.until(EC.presence_of_element_located((By.XPATH, "//button[@type='submit']")))
        self.assertEqual(save_button.text, "Zapisz")
        self.browser.execute_script("arguments[0].scrollIntoView(true);", save_button)
        save_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
        save_button.click()
        # 11. User is redirected to proper page and added article with proper formatting is shown
        self.assertEqual(self.browser.current_url, edit_link_url)
        self.assertTrue('Test title' in self.browser.page_source)
        self.assertTrue('<strong>Bold </strong>' in self.browser.page_source)
        self.assertTrue('<td>row 0, cell 0</td>' in self.browser.page_source)
        self.assertTrue('<td>row 2, cell 5</td>' in self.browser.page_source)
        # 12. User quits the browser

    # # TODO
    # def test_photo_addition_in_ckeditor(self):
    #     # Fixture:
    #     # 1. User logs into admin panel,
    #     # 2. clicks on random page edit link,
    #     # 3. clicks on "Add new article" button
    #     # Actual test:
    #     # 1. User clicks on ckeditor's add image button
    #     # 2. User selects an image from local disc
    #     # 3. User clicks on "Save" button
    #     # 4. User is redirected with corresponding page
    #     # 5. Previously added image is presented on the page
    #     pass

    def test_edit_page_for_all_pages_are_present(self):
        # Fixture:
        # 1. User logs into admin panel
        self.login_admin()
        # Actual test:
        # 1. For every edit page link:
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//ul/li[@class='page_name']/a")))
        edit_links = self.browser.find_elements(By.XPATH, "//ul/li[@class='page_name']/a")
        edit_link_texts = [l.text for l in edit_links]
        self.browser.maximize_window()
        for edit_link_text in edit_link_texts:
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//ul/li[@class='page_name']/a")))
            edit_links = self.browser.find_elements(By.XPATH, "//ul/li[@class='page_name']/a")
            edit_link = [l for l in edit_links if l.text == edit_link_text][0]
            #   * Click on the link
            edit_link.click()
            ckeditor = self.wait.until(EC.presence_of_element_located((By.ID, 'cke_id_content')))
            header = self.browser.find_element(By.ID, "edit_page_title")
            #   * Check if edit page is presented
            self.assertEqual(header.text, edit_link_text)
            self.assertTrue(ckeditor)
            #   * Go back
            self.browser.back()
            #   * Select next link
        # 2. Quit browser

    def test_page_selection_for_articles(self):
        # Fixture:
        # 1. User logs into admin panel
        self.login_admin()
        # 2. User clicks on main site's edit page link
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//ul/li[@class='page_name']/a")))
        edit_links = self.browser.find_elements(By.XPATH, "//ul/li[@class='page_name']/a")
        main_page_edit_link = [link for link in edit_links if link.text == "Główna"][0]
        main_page_edit_link.click()
        # 3. User clicks on "Add new article" button
        add_new_article_button = self.wait.until(EC.presence_of_element_located((By.ID, 'add_new')))
        add_new_article_button.click()
        # Actual test:
        # 1. There is no option to select other pages for article to appear
        self.wait.until(EC.presence_of_element_located((By.ID, "edit_page_title")))
        page_selection = self.browser.find_elements(By.ID, "id_page")
        self.assertFalse(page_selection)

    def test_edit_option_present(self):
        # Fixture:
        # 1. User logs into admin panel
        self.login_admin()
        # 2. User adds an article to main page and saves it
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//ul/li[@class='page_name']/a")))
        edit_links = self.browser.find_elements(By.XPATH, "//ul/li[@class='page_name']/a")
        main_page_edit_link = [link for link in edit_links if link.text == "Główna"][0]
        main_page_edit_link.click()
        add_new_article_button = self.wait.until(EC.presence_of_element_located((By.ID, 'add_new')))
        add_new_article_button.click()
        title_field = self.browser.find_element(By.ID, "id_title")
        title_field.send_keys("Test title")
        ckeditor_form = self.browser.find_element(By.ID, "cke_id_content")
        content_form = self.browser.find_element(By.XPATH, "/html/body")
        ckeditor_form.click()
        content_form.send_keys('Test content')
        save_button = self.wait.until(EC.presence_of_element_located((By.XPATH, "//button[@type='submit']")))
        self.browser.maximize_window()
        save_button.click()
        # Actual test:
        # 1. Previously added article is displayed correctly
        self.assertTrue("Test title" in self.browser.page_source)
        self.assertTrue("Test content" in self.browser.page_source)
        # 2. Edit button is present next to the article
        edit_button = self.browser.find_element(By.ID, "edit_button")
        self.assertTrue(edit_button)
        # 3. User clicks on edit button
        edit_button.click()
        # 4. User is presented with a edit page with previously added article in edit mode
        self.assertTrue("Test title" in self.browser.page_source)
        self.assertTrue("Test content" in self.browser.page_source)
        # 5. User changes the content
        self.wait.until(EC.presence_of_element_located((By.ID, 'cke_id_content')))
        ckeditor_form = self.browser.find_element(By.ID, "cke_id_content")
        content_form = self.browser.find_element(By.XPATH, "/html/body")
        ckeditor_form.click()
        content_form.send_keys(' changed')
        # 6. User clicks on the "Save" button
        save_button = self.wait.until(EC.presence_of_element_located((By.XPATH, "//button[@type='submit']")))
        save_button.click()
        # 7. User is redirected to main site's edit page where article with changed content is presented
        self.assertTrue('changed' in self.browser.page_source)

    def test_show_on_whiteboard_option(self):
        # Fixture:
        # 1. User logs into admin panel
        self.login_admin()
        # 2. User goes to the news site's edit page
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//ul/li[@class='page_name']/a")))
        edit_links = self.browser.find_elements(By.XPATH, "//ul/li[@class='page_name']/a")
        news_page_edit_link = [link for link in edit_links if link.text == "Aktualności"][0]
        news_page_edit_link.click()
        # 3. User clicks on "Add new article" button
        add_new_article_button = self.wait.until(EC.presence_of_element_located((By.ID, 'add_new')))
        add_new_article_button.click()
        # 4. User is presented with add article interface (ckeditor)
        # 5. User enters title and content
        title_field = self.browser.find_element(By.ID, "id_title")
        title_field.send_keys("Test title")
        ckeditor_form = self.browser.find_element(By.ID, "cke_id_content")
        content_form = self.browser.find_element(By.XPATH, "/html/body")
        ckeditor_form.click()
        content_form.send_keys('Test content')
        # Actual test:
        # 1. There is a checkbox "Show on main page's whiteboard"
        # 2. User checks the checkbox "Show on main page's whiteboard"
        self.browser.maximize_window()
        self.wait.until(EC.presence_of_element_located((By.ID, "show_on_whiteboard")))
        whiteboard_checkbox = self.browser.find_element(By.ID, "show_on_whiteboard")
        whiteboard_checkbox.click()
        # 3. User clicks on "Save" button
        save_button = self.wait.until(EC.presence_of_element_located((By.XPATH, "//button[@type='submit']")))
        save_button.click()
        # 4. User is redirected to news site's edit page
        self.wait.until(EC.presence_of_element_located((By.ID, "edit_page_title")))
        # 5. Previously added article is presented on the page
        self.assertTrue("Test title" in self.browser.page_source)
        self.assertTrue("Test content" in self.browser.page_source)
        # 6. User goes to main page
        self.browser.get(self.live_server_url)
        # 7. Green whiteboard is presented on the page with links to previously added article on news page
        whiteboard = self.wait.until(EC.presence_of_element_located((By.ID, "whiteboard")))
        # 8. User clicks on the link on the whiteboard
        whiteboard_links = whiteboard.find_elements(By.TAG_NAME, "a")
        link_url = whiteboard_links[0].get_attribute("href")
        article_id = link_url.split('/')[4]
        whiteboard_links[0].click()
        # 9. Link redirects user to the news page and anchor for previously added article
        self.assertEqual(self.browser.current_url, f"{self.live_server_url}/{DEFAULT_PAGES['Aktualności']['url']}{article_id}")

    def test_whiteboard_present_on_index_page(self):
        # Fixture:
        # 1. User logs into admin panel
        self.login_admin()
        # 2. User goes to the news site's edit page
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//ul/li[@class='page_name']/a")))
        edit_links = self.browser.find_elements(By.XPATH, "//ul/li[@class='page_name']/a")
        news_page_edit_link = [link for link in edit_links if link.text == "Aktualności"][0]
        news_page_edit_link.click()
        # 3. User adds new article for news page and checks the checkbox for it to be presented on whiteboard
        add_new_article_button = self.wait.until(EC.presence_of_element_located((By.ID, 'add_new')))
        add_new_article_button.click()
        title_field = self.browser.find_element(By.ID, "id_title")
        title_field.send_keys("Test title")
        ckeditor_form = self.browser.find_element(By.ID, "cke_id_content")
        content_form = self.browser.find_element(By.XPATH, "/html/body")
        ckeditor_form.click()
        content_form.send_keys('Test content')
        self.browser.maximize_window()
        whiteboard_checkbox = self.browser.find_element(By.ID, "show_on_whiteboard")
        whiteboard_checkbox.click()

        save_button = self.wait.until(EC.presence_of_element_located((By.XPATH, "//button[@type='submit']")))
        save_button.click()
        # Actual test:
        # 1. User goes to main page
        self.browser.get(self.live_server_url)
        # 2. Green whiteboard is presented on the page with links to previously added article on news page
        whiteboard = self.wait.until(EC.presence_of_element_located((By.ID, "whiteboard")))
        # 3. User clicks on the link on the whiteboard
        whiteboard_links = whiteboard.find_elements(By.TAG_NAME, "a")
        link_url = whiteboard_links[0].get_attribute("href")
        article_id = link_url.split('/')[4]
        whiteboard_links[0].click()
        # 4. Link redirects user to the news page and anchor for previously added article
        self.assertEqual(self.browser.current_url, f"{self.live_server_url}/{DEFAULT_PAGES['Aktualności']['url']}{article_id}")

    def test_deleting_articles(self):
        # Fixture:
        # 1. User logs into admin panel
        self.login_admin()
        # 2. User goes to the news site's edit page
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//ul/li[@class='page_name']/a")))
        edit_links = self.browser.find_elements(By.XPATH, "//ul/li[@class='page_name']/a")
        news_page_edit_link = [link for link in edit_links if link.text == "Aktualności"][0]
        news_page_edit_link.click()
        # 3. User adds new article on news site
        add_new_article_button = self.wait.until(EC.presence_of_element_located((By.ID, 'add_new')))
        add_new_article_button.click()
        title_field = self.browser.find_element(By.ID, "id_title")
        title_field.send_keys("Test title")
        ckeditor_form = self.browser.find_element(By.ID, "cke_id_content")
        content_form = self.browser.find_element(By.XPATH, "/html/body")
        ckeditor_form.click()
        content_form.send_keys('Test content')
        save_button = self.wait.until(EC.presence_of_element_located((By.XPATH, "//button[@type='submit']")))
        self.browser.maximize_window()
        save_button.click()
        # Actual test:
        # 1. User goes back to main admin panel's site
        self.browser.back()
        # 2. User clicks on link that leads to news page's edit site
        edit_links = self.browser.find_elements(By.XPATH, "//ul/li[@class='page_name']/a")
        news_page_edit_link = [link for link in edit_links if link.text == "Aktualności"][0]
        news_page_edit_link.click()
        # 3. "Delete" button is present next to previously added article
        delete_button = self.wait.until(EC.element_to_be_clickable((By.ID, "delete_button")))
        # 4. User clicks on "Delete"
        self.browser.maximize_window()
        delete_button.click()
        # 4.1 User is presented with a confirmation dialog
        self.wait.until(EC.alert_is_present())
        alert = self.browser.switch_to.alert
        alert.accept()
        # 4.2 User clicks on "OK" button
        # 5. Article is deleted and is no longer presented on the edit page
        time.sleep(2)
        self.wait.until(EC.presence_of_element_located((By.ID, "edit_page_title")))
        self.assertFalse("Test title" in self.browser.page_source)
        # 6. User clicks on "show page" button in the navigation bar and is redirected to News site
        show_page_button = self.wait.until(EC.presence_of_element_located((By.XPATH, "//a[@class='nav-link admin_welcome' and text()='Zobacz stronę']")))
        show_page_button.click()
        # 7. Deleted article is not presented on the page
        self.assertFalse("Test title" in self.browser.page_source)
        self.browser.quit()
