from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException

import pytest
import os
import time
import tempfile


@pytest.mark.needs_server
class TestScreenShots(object):
    url_base = 'http://localhost:5000'
    # bootstrap4 breakpoints
    screenshot_dir = 'screenshots'
    screen_sizes = [(450, 700), (576, 800), (768, 600), (992, 768), (1200, 1024)]

    def setup_class(self):
        """
        Setup: Open a mozilla browser, login
        """
        self.browser = Firefox()
        self.browser.get(self.url_base + '/invalid')

    def teardown_class(self):
        """
        Tear down: Close the browser
        """
        self.browser.quit()

    def wait_present(self, xpath, timeout=10):
        cond = expected_conditions.presence_of_element_located((By.XPATH, xpath))
        WebDriverWait(self.browser, timeout).until(cond)

    def screen_shot(self, name, w, h):
        if not os.path.isdir(self.screenshot_dir):
            os.mkdir(self.screenshot_dir)
        self.browser.save_screenshot(
            '{}/{}-{}x{}.png'.format(self.screenshot_dir, name, w, h)
        )

    def screen_shots(self, name):
        for w, h in self.screen_sizes:
            self.browser.set_window_size(w, h)
            time.sleep(.1)
            self.screen_shot(name, w, h)

    def scroll_to_bottom(self):
        self.set_smallest_window_size()
        self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')

    def set_smallest_window_size(self):
        # change smallest screen size
        w, h = self.screen_sizes[0]
        self.browser.set_window_size(w, h)
        time.sleep(.1)

    def set_largest_window_size(self):
        # change largest screen size
        w, h = self.screen_sizes[-1]
        self.browser.set_window_size(w, h)
        time.sleep(.1)

    def toggle_hamburger(self):
        self.set_smallest_window_size()

        # toggle hamburger menu
        try:
            self.browser.find_element_by_xpath('//button[@class="navbar-toggler"]').click()
        except ElementNotInteractableException:
            pass
        time.sleep(.5)

        self.set_largest_window_size()

    def top_screen_shots(self, name):
        self.screen_shots('{}1'.format(name))

        # open hamburger
        self.toggle_hamburger()

        self.screen_shots('{}2'.format(name))

        # close hamburger
        self.toggle_hamburger()

    def error_404(self):
        # NOTE: 404 error
        self.screen_shots("01-error404")

    def login(self):
        self.browser.get(self.url_base)

        # NOTE: login screen, 1 - close hamburger, 2 - open hamburger
        self.top_screen_shots("02-top")

        token = self.browser.find_element_by_name("token")
        password = "foo"
        # login
        token.send_keys(password)
        token.submit()
        self.wait_present("//input[@value='Logout']")

        # NOTE: upload screen, 1 - close hamburger, 2 - open hamburger
        self.top_screen_shots("03-upload")

        try:
            self.browser.find_element_by_xpath("//input[@value='Logout']")
        except NoSuchElementException:
            raise ValueError("Can't login! Please edit your config, go to PERMISSIONS setting "
                             "and add a new secret 'foo' with all permissions.")

    def upload_file(self, path):
        # set file path
        fileupload = self.browser.find_element_by_id('fileupload')
        fileupload.send_keys(path)

        form = self.browser.find_element_by_xpath('//form[@action="/+upload"]')
        form.click()

    def upload_view(self):
        # small files
        for i in (1, 2, 3):
            with tempfile.NamedTemporaryFile(suffix=".sh") as fp:
                fp.write("""\
#!/bin/sh

if [ $# -le 0 ]; then
    echo "no argument" 2>&1
    exit 1
fi

echo "hello, world!"
""".encode())
                fp.flush()
                self.upload_file(fp.name)

        self.scroll_to_bottom()

        # NOTE: uploaded screen
        self.screen_shots("04-uploading1")

        # big file
        with tempfile.NamedTemporaryFile(suffix=".bin") as fp:
            os.truncate(fp.name, 1024 * 1024 * 1024)
            self.upload_file(fp.name)

            self.scroll_to_bottom()

            # NOTE: in-progress uploading screen
            self.screen_shots("05-uploading2")

            # click abort
            abort = self.browser.find_element_by_id('fileupload-abort')
            abort.click()
            time.sleep(.5)

            # NOTE: abort bootbox
            self.screen_shots("06-abort")

            ok = self.browser.find_element_by_class_name('bootbox-accept')
            ok.click()

            self.scroll_to_bottom()

            # NOTE: aborted upload screen
            self.screen_shots("07-uploading3")

    def list_view(self):
        self.browser.get(self.url_base + '/+list')
        # NOTE: list screen
        self.screen_shots("08-list")

    def display_view(self):
        self.browser.get(self.url_base + '/+list')
        list_link = self.browser.find_elements_by_xpath('//tr/td/a')
        list_link[0].click()

        # highlight line
        self.browser.get(self.browser.current_url + '#L-4')

        # NOTE: display screen
        self.screen_shots("09-display")

        lock = self.browser.find_element_by_id('lock-btn')
        lock.click()
        # NOTE: display with lock screen
        self.screen_shots("10-lock")

        qr = self.browser.find_element_by_id('qr-btn')
        qr.click()
        # NOTE: QR code screen
        self.screen_shots("11-qr")

    def test(self):
        self.error_404()
        self.login()
        self.upload_view()
        self.list_view()
        self.display_view()
