"""
Testing Facebook and Facebook flow.

donkies.com - development (setup /etc/hosts)
donkies.co (app.donkies.co)  - production

PERMISSIONS
https://developers.facebook.com/docs/facebook-login/permissions

public_profile (Default)

id
cover
name
first_name
last_name
age_range
link
gender
locale
picture
timezone
updated_time
verified

"Facebook Login" -> "Settings" -> "Client OAuth Login" should be turned on.

Values that requested from Facebook Graph using access_token passed in string.
Method: user.get_facebook_user implements it.


PREPARATION:

1) Create test app on https://developers.facebook.com
2) Settings basics - set "donkies.com" to "App Domains"
3) Add platform: Web
4) Set in "Website" -> "Site URL": http://donkies.com/
5) The app should have access to user's email (by default)
6) "Roles" -> "Test Users" - create test user.
7) "PRODUCTS" -> Add product: "Facebook Login"
8) "PRODUCTS" -> "Facebook Login" -> "Settings"
   set "Valid OAuth redirect URIs"
   http://donkies.com:8080/login_facebook

USAGE:

1) Frontend redirect user to Facebook auth:
   https://www.facebook.com/dialog/oauth?client_id={APP_ID}&redirect_uri={REDIRECT_URI}
2) In tests: all we need is code that passed as GET param.

3) In frontend (on redirect_uri). Frontend get "code" in GET param
   and send request to API.
   It should get "token" and 200 if success, otherwise 400 error.

TEST DATA:

User name: Rick Alagagejadhai Occhinowitz
User ID: 100017175014819
Email: dmakbyslnm_1495136332@tfbnw.net
Password: aaavvv111

Use selenium webdriver to automate login flow.
"""

import json
import os
import re
import pytest
from selenium import webdriver
from django.conf import settings
from .import base
from web.models import User, Token


class TestFacebook(base.Mixin):
    TEST_USER_EMAIL = 'dmakbyslnm_1495136332@tfbnw.net'
    TEST_USER_PASSWORD = 'aaavvv111'

    def get_code(self):
        """
        Use real browser to get "code".
        1) Go to dialog page (login page).
        2) Auth with test user.
        3) Get "code" from url params.
        4) Use code to request API.
           "code" is valid only for single test run.
        """
        chromedriver = '/home/vlad/dev/ubuntu/chromedriver'
        os.environ['webdriver.chrome.driver'] = chromedriver
        br = webdriver.Chrome(chromedriver)

        url = 'https://www.facebook.com/dialog/oauth?client_id={}'
        url += '&redirect_uri={}'
        url = url.format(
            settings.FACEBOOK_APP_ID, settings.FACEBOOK_REDIRECT_URI)
        br.get(url)

        el = br.find_element_by_name('email')
        el.send_keys(self.TEST_USER_EMAIL)

        el = br.find_element_by_name('pass')
        el.send_keys(self.TEST_USER_PASSWORD)

        button = br.find_element_by_id('loginbutton')
        button.click()

        m = re.search('code=(.*?)$', br.current_url)
        code = m.group(1)
        br.quit()
        return code

    @pytest.mark.django_db
    def test01(self, client):
        dic = User.get_facebook_user(
            self.get_code(), settings.FACEBOOK_REDIRECT_URI)
        print(dic)

    @pytest.mark.django_db
    def test02(self, client):
        """
        Use correct code.
        Should get success.
        """
        url = '/v1/auth/facebook'
        dic = {'code': self.get_code()}
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 200

        key = response.json()['token']
        token = Token.objects.get(key=key)
        user = token.user
        assert user.fb_id is not None
        assert user.fb_token != ''
        assert user.fb_link != ''
        assert user.fb_name != ''
        assert user.fb_first_name != ''
        assert user.fb_last_name != ''
        assert user.fb_gender != ''
        assert user.fb_locale != ''
        assert user.fb_age_range > 0
        assert user.fb_timezone > 0
        assert user.profile_image != ''

    @pytest.mark.django_db
    def test03(self, client):
        """
        Test facebook auth endpoint with wrong code.
        Should get error.
        """
        url = '/v1/auth/facebook'
        dic = {'code': 'wrong code'}
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        # print(response.content)
        assert response.status_code == 400

    @pytest.mark.django_db
    def test04(self, client):
        """
        Test facebook auth endpoint with wrong redirect_uri.
        Should get error.
        """
        url = '/v1/auth/facebook'
        dic = {'code': 'wrong code'}
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        # print(response.content)
        assert response.status_code == 400
