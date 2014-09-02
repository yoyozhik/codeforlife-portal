from django.conf import settings
from selenium import webdriver

from base import BasePage

class HelpPage(BasePage):
    def __init__(self, browser):
        super(HelpPage, self).__init__(browser)

        self.browser.find_element_by_id('help_page')
