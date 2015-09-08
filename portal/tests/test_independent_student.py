# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2015, Ocado Limited
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ADDITIONAL TERMS – Section 7 GNU General Public Licence
#
# This licence does not grant any right, title or interest in any “Ocado” logos,
# trade names or the trademark “Ocado” or any other trademarks or domain names
# owned by Ocado Innovation Limited or the Ocado group of companies or any other
# distinctive brand features of “Ocado” as may be secured from time to time. You
# must not distribute any modification of this program using the trademark
# “Ocado” or claim any affiliation or association with Ocado or its employees.
#
# You are not authorised to use the name Ocado (or any of its trade names) or
# the names of any author or contributor in advertising or for publicity purposes
# pertaining to the distribution of this program, without the prior written
# authorisation of Ocado.
#
# Any propagation, distribution or conveyance of this program must include this
# copyright notice and these terms. You must not misrepresent the origins of this
# program; modified versions of the program must be marked as such and not
# identified as the original program.
import re
from base_test import BaseTest
from django.core import mail
from selenium.webdriver.support.wait import WebDriverWait


from portal.tests.pageObjects.portal.home_page import HomePage
from utils.student import create_independent_student
from utils.messages import is_email_verified_message_showing
from utils import email as email_utils

class TestIndependentStudent(BaseTest):
    def test_signup(self):
        self.browser.get(self.live_server_url)
        page = HomePage(self.browser)
        page, _, _, _, _ = create_independent_student(page)
        assert is_email_verified_message_showing(self.browser)

    def test_login_failure(self):
        self.browser.get(self.live_server_url)
        page = HomePage(self.browser)
        page = page.go_to_play_page()
        page = page.independent_student_login_failure('Non existant username', 'Incorrect password')

        assert page.has_independent_student_login_failed()

    def test_login_success(self):
        self.browser.get(self.live_server_url)
        page = HomePage(self.browser)
        page, name, username, email, password = create_independent_student(page)
        page = page.independent_student_login(username, password)
        assert page.__class__.__name__ == 'PlayDashboardPage'

        page = page.go_to_account_page()
        assert page.check_account_details({
            'name': name
        })

    def test_reset_password(self):

        self.browser.get(self.live_server_url)
        homepage = HomePage(self.browser)

        username = create_independent_student(homepage)[2]
        page = self.get_to_forgotten_password_page()

        page.reset_username_submit(username)

        self.wait_for_email()

        page = email_utils.follow_reset_email_link(self.browser, mail.outbox[0])

        new_password = 'AnotherPassword12'

        page.change_details({'new_password1': new_password, 'new_password2': new_password})

        self.browser.get(self.live_server_url)
        page = HomePage(self.browser).go_to_play_page().go_to_independent_form().independent_student_login(username, new_password)
        assert self.is_independent_student_details(page)

    def test_reset_password_fail(self):
        page = self.get_to_forgotten_password_page()

        fake_username = "fake_username"
        page.reset_username_submit(fake_username)

        WebDriverWait(self.browser, 2).until(lambda driver: self.browser_text_find("Cannot find an account with that username"))
        self.assertIn("Cannot find an account with that username", self.browser.page_source)

    def browser_text_find(self, text_to_find):
        text = self.browser.page_source
        result = re.search(text_to_find, text)
        if result is not None:
            return True
        else:
            return False

    def get_to_forgotten_password_page(self):
        self.browser.get(self.live_server_url)
        page = HomePage(self.browser) \
            .go_to_play_page() \
            .go_to_independent_form() \
            .go_to_forgotten_password_page()
        return page

    def is_independent_student_details(self, page):
        return page.__class__.__name__ == 'PlayDashboardPage'

    def wait_for_email(self):
        WebDriverWait(self.browser, 2).until(lambda driver: len(mail.outbox) == 1)