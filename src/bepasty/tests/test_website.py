from selenium.webdriver import Firefox
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchDriverException, NoSuchElementException
)

import pytest

import time


@pytest.mark.needs_server
class TestMaxlifeFeature:
    """
    Checks if the maxlife feature is working.
    """

    def setup_class(self):
        """
        Setup: Open a web browser and log in.
        """
        try:
            self.browser = Firefox()
        except NoSuchDriverException:
            service = ChromeService(executable_path="/usr/bin/chromedriver")
            self.browser = Chrome(service=service)
        self.browser.get('http://localhost:5000/')
        token = self.browser.find_element(By.NAME, "token")
        password = "foo"
        # Log in
        token.send_keys(password)
        token.send_keys(Keys.ENTER)
        time.sleep(.1)
        try:
            self.browser.find_element(By.XPATH, "//input[@value='Logout']")
        except NoSuchElementException:
            raise ValueError("Can't log in! Create a user 'foo' with the permissions "
                             "'read,create,delete' in your PERMISSIONS in the config.")

    def teardown_class(self):
        """
        Teardown: Close the browser.
        """
        self.browser.quit()

    @property
    def page_body_lowercase(self):
        return self.browser.find_element(By.TAG_NAME, "body").text.lower()

    def test_unit_input_exists(self):
        unit_input = self.browser.find_element(By.NAME, "maxlife-unit")
        assert unit_input is not None
        value_input = self.browser.find_element(By.NAME, "maxlife-value")
        assert value_input is not None

    def fill_form(self):
        """
        Fills test values into the form and submits it.
        :return: tuple(filename, pasted_text)
        """
        filename = "test.txt"
        text_to_paste = "This is a test"
        paste_input = self.browser.find_element(By.ID, "formupload")
        paste_input.send_keys(text_to_paste)
        filename_input = self.browser.find_element(By.ID, "filename")
        filename_input.send_keys(filename)
        contenttype_input = self.browser.find_element(By.ID, "contenttype")
        contenttype_input.send_keys("text/plain")
        contenttype_input.send_keys(Keys.ENTER)
        time.sleep(.2)  # give some time to render the next view
        return filename, text_to_paste

    def delete_current_file(self):
        self.browser.find_element(By.ID, "del-btn").click()
        time.sleep(.2)
        self.browser.find_element(By.CLASS_NAME, "bootbox-accept").click()

    def test_paste_keep_forever(self):
        self.browser.find_element(By.XPATH, "//select[@name='maxlife-unit']/option[@value='forever']").click()
        value_input = self.browser.find_element(By.NAME, "maxlife-value")
        value_input.clear()
        value_input.send_keys(1)
        self.fill_form()
        assert "max lifetime: forever" in self.page_body_lowercase
        self.delete_current_file()

    def test_paste_keep_minutes(self):
        self.browser.find_element(By.XPATH, "//select[@name='maxlife-unit']/option[@value='minutes']").click()
        value_input = self.browser.find_element(By.NAME, "maxlife-value")
        value_input.clear()
        value_input.send_keys(1)
        self.fill_form()
        assert "max lifetime: forever" not in self.page_body_lowercase
        self.delete_current_file()

    def test_filename_gets_displayed(self):
        filename, _ = self.fill_form()
        assert filename.lower() in self.page_body_lowercase
        self.delete_current_file()

    def test_pasted_text_gets_displayed(self):
        _, pasted_text = self.fill_form()
        self.browser.find_element(By.ID, "inline-btn").click()
        assert pasted_text.lower() in self.page_body_lowercase
        self.browser.back()
        self.delete_current_file()

    @pytest.mark.slow
    def test_file_gets_deleted_after_expiry_time(self):
        self.browser.find_element(By.XPATH, "//select[@name='maxlife-unit']/option[@value='minutes']").click()
        value_input = self.browser.find_element(By.NAME, "maxlife-value")
        value_input.clear()
        value_input.send_keys(1)
        self.fill_form()
        time.sleep(61)
        self.browser.find_element(By.ID, "inline-btn").click()
        assert "not found" in self.page_body_lowercase
