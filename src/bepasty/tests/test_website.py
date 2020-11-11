from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

import pytest

import time


@pytest.mark.needs_server
class TestMaxlifeFeature(object):
    """
    Checks if the maxlife feature is working
    """

    def setup_class(self):
        """
        Setup: Open a mozilla browser, login
        """
        self.browser = Firefox()
        self.browser.get('http://localhost:5000/')
        token = self.browser.find_element_by_name("token")
        password = "foo"
        # login
        token.send_keys(password)
        token.send_keys(Keys.ENTER)
        time.sleep(.1)
        try:
            self.browser.find_element_by_xpath("//input[@value='Logout']")
        except NoSuchElementException:
            raise ValueError("Can't login!!! Create a user 'foo' with the permissions"
                             "'read' and 'create' in your PERMISSIONS in the config")

    def teardown_class(self):
        """
        Tear down: Close the browser
        """
        self.browser.quit()

    @property
    def page_body_lowercase(self):
        return self.browser.find_element_by_tag_name("body").text.lower()

    def test_unit_input_exists(self):
        unit_input = self.browser.find_element_by_name("maxlife-unit")
        assert unit_input is not None
        value_input = self.browser.find_element_by_name("maxlife-value")
        assert value_input is not None

    def fill_form(self):
        """
        Fills test values to the form and submits it
        :return: tuple(filename, pasted_text)
        """
        filename = "test.txt"
        text_to_paste = "This is test"
        paste_input = self.browser.find_element_by_id("formupload")
        paste_input.send_keys(text_to_paste)
        filename_input = self.browser.find_element_by_id("filename")
        filename_input.send_keys(filename)
        contenttype_input = self.browser.find_element_by_id("contenttype")
        contenttype_input.send_keys("text/plain")
        contenttype_input.send_keys(Keys.ENTER)
        time.sleep(.2)  # give some time to render next view
        return filename, text_to_paste

    def delete_current_file(self):
        self.browser.find_element_by_id("del-btn").click()
        time.sleep(.2)
        self.browser.find_element_by_class_name("bootbox-accept").click()

    def test_paste_keep_forever(self):
        self.browser.find_element_by_xpath("//select[@name='maxlife-unit']/option[@value='forever']").click()
        value_input = self.browser.find_element_by_name("maxlife-value")
        value_input.clear()
        value_input.send_keys(1)
        self.fill_form()
        assert "max lifetime: forever" in self.page_body_lowercase
        self.delete_current_file()

    def test_paste_keep_minutes(self):
        self.browser.find_element_by_xpath("//select[@name='maxlife-unit']/option[@value='minutes']").click()
        value_input = self.browser.find_element_by_name("maxlife-value")
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
        self.browser.find_element_by_id("inline-btn").click()
        assert pasted_text.lower() in self.page_body_lowercase
        self.browser.back()
        self.delete_current_file()

    @pytest.mark.slow
    def test_file_gets_deleted_after_expiry_time(self):
        self.browser.find_element_by_xpath("//select[@name='maxlife-unit']/option[@value='minutes']").click()
        value_input = self.browser.find_element_by_name("maxlife-value")
        value_input.clear()
        value_input.send_keys(1)
        self.fill_form()
        time.sleep(61)
        self.browser.find_element_by_id("inline-btn").click()
        assert "not found" in self.page_body_lowercase
