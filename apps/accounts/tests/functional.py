# -*- coding: utf8 -*-
"""
Functional tests using Selenium.

See: ``docs/testing/selenium.rst`` for details.
"""
import time
import re
import datetime

from django.contrib.auth.hashers import check_password
from django.contrib.sites.models import Site
from django.conf import settings
from django.core import mail
from django.utils.unittest.case import skipUnless, skipIf

from bluebottle.tests.utils import SeleniumTestCase, css_dict
from apps.geo.models import Region
from ..models import BlueBottleUser



@skipUnless(getattr(settings, 'SELENIUM_TESTS', False),
        'Selenium tests disabled. Set SELENIUM_TESTS = True in your settings.py to enable.')
class AccountSeleniumTests(SeleniumTestCase):
    """
    Selenium tests for account actions.
    """
    def setUp(self):
        pass

    def test_signup(self):
        """
        Test become member signup.

        1. Visit signup page
        2. Fill in form
        3. Click signup button
        4. Receive activation link by mail
        5. Visit activation link
        6. Validate that user is active
        """
        self.visit_homepage()

        # Find the link to the signup button page and click it.
        self.browser.find_link_by_partial_text('Signup').first.click()

        # Validate that we are on the intended page.
        self.assertTrue(self.browser.is_text_present('BECOME A 1%MEMBER', wait_time=10),
                'Cannot load the signup page.'),

        self.assertEqual(self.browser.url, '%s/en/#/signup' % self.live_server_url)
        self.assertEqual(self.browser.title, '1%Club')

        # NOTE: Most ember elements don't have meaningfull names. This makes it hard to find out which element is the
        # correct one.
        form = self.browser.find_by_css('form.form-signup').first

        # Fill in the form.
        form_data = {
            'input[placeholder="First name"]': 'John',
            'input[placeholder="Surname"]': 'Doe',
            'input[type="email"]': 'johndoe@example.com',
            'input[type="password"]': 'secret'
        }
        self.browser.fill_form_by_css(form, form_data)

        # Make sure we have an empty mailbox and the user doesn't exist yet.
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(BlueBottleUser.objects.filter(email='johndoe@example.com').count(), 0)

        # Click the signup button within the form.
        form.find_by_css('button').first.click()

        # After signing up, a message should appear
        self.assertTrue(self.browser.is_text_present('THANKS FOR SIGNING UP!', wait_time=10))

        # And a user should be created.
        self.assertEqual(BlueBottleUser.objects.filter(email='johndoe@example.com').count(), 1)
        user = BlueBottleUser.objects.get(email='johndoe@example.com')
        self.assertFalse(user.is_active)

        # And a mail should be sent to the just signed up email address.
        self.assertEqual(len(mail.outbox), 1)
        activation_mail = mail.outbox[0]

        self.assertEqual(activation_mail.subject, 'Welcome to 1%CLUB')
        self.assertIn(user.email, activation_mail.to)

        # Extract activation link and change domain for the test.
        activation_link = re.findall('href="([a-z\:\.\/\#]+\/activate\/[^"]+)', activation_mail.body)[0]

        current_site = Site.objects.get_current()

        self.assertTrue(current_site.domain in activation_link)
        activation_link = activation_link.replace(current_site.domain, self.live_server_url[7:])

        # Visit the activation link.
        self.browser.visit(activation_link)

        # TODO: After visiting the link, the website is shown in Dutch again.
        self.assertTrue(self.browser.is_text_present('Hurray!', wait_time=10))

        # Reload the user.
        user = BlueBottleUser.objects.get(pk=user.pk)
        self.assertTrue(user.is_active)

    def test_login(self):
        """
        Test user can login.
        """
        # Create and activate user.
        user = BlueBottleUser.objects.create_user('johndoe@example.com', 'secret')

        self.visit_homepage()

        # Find the link to the login button page and click it.
        self.browser.find_link_by_text('Login').first.click()

        # Validate that we are on the intended page.
        self.assertTrue(self.browser.is_text_present('LOG IN', wait_time=10),
                'Cannot load the login popup.'),

        # Fill in details.
        self.browser.fill('username', user.email)
        self.browser.fill('password', 'secret')

        self.browser.find_by_value('Login').first.click()

        self.assertTrue(self.browser.is_text_present('MY 1%', wait_time=10))

    @skipIf(settings.SELENIUM_WEBDRIVER=='firefox', 'Firefox does not support mouse interactions.')
    def test_edit_profile(self):
        # Create and activate user.
        user = BlueBottleUser.objects.create_user('johndoe@example.com', 'secret')
        
        self.login(user.email, 'secret')

        self.browser.find_by_css('.nav-member-my1percent').first.mouse_over()
        self.browser.find_link_by_partial_text('Edit my profile & settings').first.click()

        # Validate that we are on the intended page.
        self.assertTrue(self.browser.is_text_present('EDIT YOUR PROFILE', wait_time=10))

        form = self.browser.find_by_tag('form').first

        # Fill in the form.
        self.browser.fill_form_by_label(form, [
            ('Name', ['John', 'Doe']),
            ('Profile Picture', None),
            ('About Yourself', 'I am John Doe.'),
            ('Why are you a member?', 'Because I care.'),
            ('Your website', 'http://www.onepercentclub.com'),
            ('Location', 'Amsterdam'),
            ('Time available', '5-8_hours_week')
        ])

        form.find_by_css('button').first.click()

        # Validate with the message.
        self.assertTrue(self.browser.is_text_present('Profile saved', wait_time=10))

        # Reload the user.
        user = BlueBottleUser.objects.get(pk=user.pk)
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.about, 'I am John Doe.')
        self.assertEqual(user.why, 'Because I care.')
        self.assertEqual(user.website, 'http://www.onepercentclub.com')
        self.assertEqual(user.location, 'Amsterdam')
        self.assertEqual(user.availability, '5-8_hours_week')

    @skipIf(settings.SELENIUM_WEBDRIVER=='firefox', 'Firefox does not support mouse interactions.')
    def test_edit_account(self):
        # Create and activate user.
        user = BlueBottleUser.objects.create_user('johndoe@example.com', 'secret')
        # Create a country.
        region = Region.objects.create(name='Europe', numeric_code='150')
        subregion = region.subregion_set.create(name='Western Europe', numeric_code='155')
        country = subregion.country_set.create(name='Netherlands', numeric_code='528', alpha2_code='NL', alpha3_code='NLD')

        self.login(user.email, 'secret')

        self.browser.find_by_css('.nav-member-my1percent').first.mouse_over()
        self.browser.find_link_by_partial_text('Edit my profile & settings').first.click()

        # Validate that we are on the intended page.
        self.assertTrue(self.browser.is_text_present('EDIT YOUR PROFILE', wait_time=10))

        # Navigate to account settings.
        self.browser.find_link_by_itext('ACCOUNT\nSETTINGS').first.click()

        # Validate that we are on the intended page.
        self.assertTrue(self.browser.is_text_present('EDIT YOUR ACCOUNT', wait_time=10))

        # Validate current values.
        fieldsets = self.browser.find_by_css('form fieldset')
        self.assertEqual(len(fieldsets), 4)

        # Fill in all fieldsets.
        self.browser.fill_form_by_label(fieldsets[0], [
            ('Email Address', 'doejohn@example.com'),
        ])
        self.browser.fill_form_by_label(fieldsets[1], [
            ('I\'d like to receive email about', True),
        ])
        self.browser.fill_form_by_label(fieldsets[2], [
            ('Account type', 'person'),
            ('I want to share', [True, True]),
        ])
        self.browser.fill_form_by_label(fieldsets[3], [
            ('Address Line 1', 'Example street 1'),
            ('Address Line 2', ''),
            ('City', 'Amsterdam'),
            ('Province / State', 'North-Holland'),
            ('Postal Code', '1234 AB'),
            ('Country', 'NL'),
            ('Gender', [None, 'male', None]),
            ('Date of birth', '01/01/1980')
        ])

        self.browser.find_link_by_itext('SAVE').first.click()

        # Validate with the message.
        self.assertTrue(self.browser.is_text_present('Account settings saved', wait_time=10))

        # Reload and validate the user.
        user = BlueBottleUser.objects.get(pk=user.pk)
        self.assertEqual(user.email, 'doejohn@example.com')
        self.assertEqual(user.gender, 'male')
        self.assertTrue(user.share_money)
        self.assertTrue(user.share_time_knowledge)
        self.assertTrue(user.newsletter)
        self.assertEqual(user.birthdate, datetime.date(1980, 1, 1))

        self.assertEqual(user.address.line1, 'Example street 1')
        self.assertEqual(user.address.line2, '')
        self.assertEqual(user.address.city, 'Amsterdam')
        self.assertEqual(user.address.state, 'North-Holland')
        # TODO: This does not work yet (#453).
        self.assertEqual(user.address.country, country)
        self.assertEqual(user.address.postal_code, '1234 AB')

    def test_forgot_password(self):
        # Create and activate user.
        old_password = 'secret'
        user = BlueBottleUser.objects.create_user('johndoe@example.com', old_password)
        self.assertTrue(check_password(old_password, user.password))

        self.visit_homepage()

        # Find the link to the login button page and click it.
        self.browser.find_link_by_text('Login').first.click()
        self.browser.find_link_by_text('I forgot my password').first.click()

        # Validate that we are on the intended page.
        self.assertTrue(self.browser.is_text_present('FORGOT YOUR PASSWORD?'))

        self.assertEqual(len(mail.outbox), 0)

        # Fill in email and hit reset.
        self.browser.find_by_css('input#passwordResetEmail').first.fill(user.email)
        self.browser.find_link_by_itext('RESET').first.click()

        # Validate that we are on the intended page.
        self.assertTrue(self.browser.is_text_present('YOU\'VE GOT MAIL!', wait_time=10))

        # Do we really have mail?
        self.assertEqual(len(mail.outbox), 1)
        reset_mail = mail.outbox[0]

        # Validate the mail
        current_site = Site.objects.get_current()

        # TODO: The email is sent in Dutch, even if I go to the English website (#448).
        #self.assertEqual(reset_mail.subject, 'Password reset for %s' % current_site.domain)
        self.assertTrue(reset_mail.subject in [
            'Wachtwoord reset voor %s' % current_site.domain,
            'Password reset for %s' % current_site.domain
        ])
        self.assertIn(user.email, reset_mail.to)

        # Extract reset link and change domain for the test.
        reset_link = re.findall('href="([a-z\:\.\/\#]+\/passwordreset\/[^"]+)', reset_mail.body)[0]
        self.assertTrue(current_site.domain in reset_link)
        reset_link = reset_link.replace(current_site.domain, self.live_server_url[7:])

        # Visit the reset link.
        self.browser.visit(reset_link)

        # Validate that we are on the intended page.
        self.assertTrue(self.browser.is_text_present('RESET YOUR PASSWORD', wait_time=10))

        # Fill in the reset form.
        new_password = 'new_secret'
        form = self.browser.find_by_css('.modal form').first
        for field in form.find_by_css('input[type="password"]'):
            field.fill(new_password)

        # TODO: Button is not part of the form.
        self.browser.find_by_css('.modal .modal-footer button').first.click()

        # Validate that we are on the intended page.
        self.assertTrue(self.browser.is_text_present('YOU DID IT!', wait_time=10))

        # Reload and validate user password in the database.
        user = BlueBottleUser.objects.get(pk=user.pk)
        self.assertFalse(check_password(old_password, user.password))
        self.assertTrue(check_password(new_password, user.password))
