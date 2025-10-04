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
class TestScreenShots:
    url_base = 'http://localhost:5000'
    # bootstrap4 breakpoints
    screenshot_dir = 'screenshots'
    screen_sizes = [(450, 700), (576, 800), (768, 600), (992, 768), (1200, 1024)]
    screenshot_seq = 1

    def setup_class(self):
        """
        Setup: Open a Mozilla Firefox browser and log in.
        """
        self.browser = Firefox()
        self.browser.get(self.url_base + '/invalid')

    def teardown_class(self):
        """
        Teardown: Close the browser.
        """
        self.browser.quit()

    def wait_present(self, xpath, timeout=10):
        cond = expected_conditions.presence_of_element_located((By.XPATH, xpath))
        WebDriverWait(self.browser, timeout).until(cond)

    def screen_shot(self, name, w, h):
        if not os.path.isdir(self.screenshot_dir):
            os.mkdir(self.screenshot_dir)
        self.browser.save_screenshot(
            '{}/{:02d}-{}-{}x{}.png'.format(self.screenshot_dir,
                                            self.screenshot_seq, name, w, h)
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
        # Change to the smallest screen size
        w, h = self.screen_sizes[0]
        self.browser.set_window_size(w, h)
        time.sleep(.1)

    def set_largest_window_size(self):
        # Change to the largest screen size
        w, h = self.screen_sizes[-1]
        self.browser.set_window_size(w, h)
        time.sleep(.1)

    def toggle_hamburger(self):
        self.set_smallest_window_size()

        # Toggle the hamburger menu
        try:
            self.browser.find_element(By.XPATH, '//button[@class="navbar-toggler"]').click()
        except ElementNotInteractableException:
            pass
        time.sleep(.5)

        self.set_largest_window_size()

    def top_screen_shots(self, name):
        self.screen_shots(f'{name}1')

        # Open the hamburger menu
        self.toggle_hamburger()

        self.screen_shots(f'{name}2')

        # Close the hamburger menu
        self.toggle_hamburger()

    def error_404(self):
        # NOTE: 404 error
        self.screen_shots("error404")
        self.screenshot_seq += 1

    def login(self):
        self.browser.get(self.url_base)

        # NOTE: login screen, 1 - hamburger closed, 2 - hamburger open
        self.top_screen_shots("top")
        self.screenshot_seq += 1

        token = self.browser.find_element(By.NAME, "token")
        password = "foo"
        # Log in
        token.send_keys(password)
        token.submit()
        self.wait_present("//input[@value='Logout']")

        # NOTE: upload screen, 1 - hamburger closed, 2 - hamburger open
        self.top_screen_shots("upload")
        self.screenshot_seq += 1

        try:
            self.browser.find_element(By.XPATH, "//input[@value='Logout']")
        except NoSuchElementException:
            raise ValueError("Can't log in! Please edit your config, go to the PERMISSIONS setting, "
                             "and add a new secret 'foo' with all permissions.")

    def upload_file(self, path):
        # Set the file path
        fileupload = self.browser.find_element(By.ID, 'fileupload')
        fileupload.send_keys(path)

        form = self.browser.find_element(By.XPATH, '//form[@action="/+upload"]')
        form.click()

    def upload_view(self):
        # Small files
        for i in (1, 2, 3):
            with tempfile.NamedTemporaryFile(suffix=".sh") as fp:
                fp.write(b"""\
#!/bin/sh

if [ $# -le 0 ]; then
    echo "no argument" 2>&1
    exit 1
fi

echo "hello, world!"
""")
                fp.flush()
                self.upload_file(fp.name)

        self.scroll_to_bottom()

        # NOTE: uploaded screen
        self.screen_shots("uploading1")

        # Large file
        with tempfile.NamedTemporaryFile(suffix=".bin") as fp:
            os.truncate(fp.name, 1024 * 1024 * 1024)
            self.upload_file(fp.name)

            self.scroll_to_bottom()

            # NOTE: in-progress uploading screen
            self.screen_shots("uploading2")
            self.screenshot_seq += 1

            # Click Abort
            abort = self.browser.find_element(By.ID, 'fileupload-abort')
            abort.click()
            time.sleep(.5)

            # NOTE: Abort Bootbox dialog
            self.screen_shots("abort")
            self.screenshot_seq += 1

            ok = self.browser.find_element(By.CLASS_NAME, 'bootbox-accept')
            ok.click()

            self.scroll_to_bottom()

            # NOTE: Aborted upload screen
            self.screen_shots("uploading3")
            self.screenshot_seq += 1

    def list_view(self):
        self.browser.get(self.url_base + '/+list')
        # NOTE: List screen
        self.screen_shots("list")
        self.screenshot_seq += 1

    def display_view(self):
        self.browser.get(self.url_base + '/+list')
        list_link = self.browser.find_elements(By.XPATH, '//tr/td/a')
        list_link[0].click()

        # Highlight a line
        self.browser.get(self.browser.current_url + '#L-4')

        # NOTE: Display screen
        self.screen_shots("display")
        self.screenshot_seq += 1

        modify = self.browser.find_element(By.ID, 'modify-btn')
        modify.click()
        time.sleep(.5)

        # NOTE: Modify Bootbox dialog
        self.screen_shots("modify")
        self.screenshot_seq += 1

        modify_cancel = self.browser.find_element(By.CLASS_NAME, 'bootbox-cancel')
        modify_cancel.click()
        time.sleep(.5)

        lock = self.browser.find_element(By.ID, 'lock-btn')
        lock.click()
        # NOTE: Display with lock screen
        self.screen_shots("lock")
        self.screenshot_seq += 1

        qr = self.browser.find_element(By.ID, 'qr-btn')
        qr.click()
        # NOTE: QR code screen
        self.screen_shots("qr")
        self.screenshot_seq += 1

    def test(self):
        self.error_404()
        self.login()
        self.upload_view()
        self.list_view()
        self.display_view()
