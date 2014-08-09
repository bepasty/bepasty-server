# Copyright: 2014 Valentin Pratz <vp.pratz@yahoo.de>
# License: BSD 2-clause, see LICENSE for details.

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
                             "'read' and 'write' in your PERMISSIONS in the config")

    def teardown_class(self):
        """
        Tear down: Close the browser
        """
        self.browser.quit()

    def test_unit_input_exists(self):
        unit_input = self.browser.find_element_by_name("maxlife-unit")
        assert unit_input is not None
        value_input = self.browser.find_element_by_name("maxlife-value")
        assert value_input is not None

    def fill_form(self):
        paste_input = self.browser.find_element_by_id("formupload")
        paste_input.send_keys("This is test")
        filename_input = self.browser.find_element_by_id("filename")
        filename_input.send_keys("test.txt")
        contenttype_input = self.browser.find_element_by_id("contenttype")
        contenttype_input.send_keys("text/plain")
        contenttype_input.send_keys(Keys.ENTER)

    def delete_current_file(self):
        self.browser.find_element_by_id("del-btn").click()
        time.sleep(.2)
        self.browser.find_element_by_class_name("btn-primary").click()

    def test_paste_keep_forever(self):
        self.browser.find_element_by_xpath("//select[@name='maxlife-unit']/option[@value='forever']").click()
        value_input = self.browser.find_element_by_name("maxlife-value")
        value_input.clear()
        value_input.send_keys(1)
        self.fill_form()
        assert "max lifetime: forever" in self.browser.find_element_by_tag_name("body").text.lower()
        self.delete_current_file()

    def test_paste_keep_minutes(self):
        self.browser.find_element_by_xpath("//select[@name='maxlife-unit']/option[@value='minutes']").click()
        value_input = self.browser.find_element_by_name("maxlife-value")
        value_input.clear()
        value_input.send_keys(1)
        self.fill_form()
        assert "max lifetime: forever" not in self.browser.find_element_by_tag_name("body").text.lower()
        self.delete_current_file()

    @pytest.mark.slow
    def test_file_gets_deleted(self):
        self.browser.find_element_by_xpath("//select[@name='maxlife-unit']/option[@value='minutes']").click()
        value_input = self.browser.find_element_by_name("maxlife-value")
        value_input.clear()
        value_input.send_keys(1)
        self.fill_form()
        time.sleep(61)
        self.browser.find_element_by_id("inline-btn").click()
        assert "not found" in self.browser.find_element_by_tag_name("body").text.lower()
