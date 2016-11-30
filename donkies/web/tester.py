import json
import time
import uuid

import django
import os
import sys

from os.path import abspath, dirname, join

path = abspath(join(dirname(abspath(__file__)), ".."))
sys.path.append(path)
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE', 'donkies.settings.development')
django.setup()
from django.conf import settings
from web.models import Token, User
from finance.models import Credentials, Member
from rest_framework.test import APIClient


class TestMember:
    """
    Tests on real local database, calling real API endpoints.
    (to test real environment.)
    Local server and celery should be run before running tests.
    """
    TEST_CODE = 'mxbank'
    TEST_USERNAME = 'test_atrium'
    TEST_PASSWORD = 'can_be_any'
    URL = settings.BACKEND_URL

    def get_auth_client(self, user):
        client = APIClient()
        token = Token.objects.get(user_id=user.id)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        return client

    def get_credentials(self):
        login = Credentials.objects.get(
            institution__code=self.TEST_CODE, field_name='LOGIN')
        password = Credentials.objects.get(
            institution__code=self.TEST_CODE, field_name='PASSWORD')
        return [
            {'field_name': login.field_name, 'value': self.TEST_USERNAME},
            {'field_name': password.field_name, 'value': self.TEST_PASSWORD},
        ]

    def signup(self):
        """
        Creates new user.
        """
        url = '{}/v1/auth/signup'.format(self.URL)
        email = '{}@gmail.com'.format(uuid.uuid4().hex)
        dic = {
            'email': email,
            'password': '12345678',
            'first_name': 'Bob',
            'last_name': 'Smith'
        }
        data = json.dumps(dic)
        client = APIClient()
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 204

        # Wait while celery task create user in atrium.
        time.sleep(3)
        user = User.objects.get(email=email)
        assert user.guid is not None
        self.user = user
        print('User created')

    def create_member(self):
        client = self.get_auth_client(self.user)
        url = '{}/v1/members'.format(self.URL)
        dic = {
            'institution_code': 'mxbank',
            'credentials': self.get_credentials()
        }
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        rd = response.json()
        self.member = Member.objects.get(identifier=rd['identifier'])
        print('Member created')

    def run(self):
        self.signup()
        self.create_member()


if __name__ == '__main__':
    # from finance.services.atrium_api import AtriumApi
    # a = AtriumApi()
    # a.search_institutions(code='mxbank')

    # tm = TestMember()
    # tm.run()
    # user = User.objects.get(email='alex@donkies.co')
    # User.objects.create_atrium_user(user.id)

    from transfer.services.dwolla_api import DwollaApi

    d = DwollaApi()
    d.test()
