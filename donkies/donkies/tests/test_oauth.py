import pytest
from rest_framework.test import APIClient
from .factories import ApplicationFactory, UserFactory
from .import base


class TestOauth(base.Mixin):
    """
    Tests for signup, signup confirm, login, password reset.
    """
    def init(self):
        # Admin
        self.admin_user = UserFactory(email='bob@gmail.com', is_admin=True)
        self.application = ApplicationFactory(user=self.admin_user)

        self.user = UserFactory(email='john@gmail.com')
        self.user.set_password('111')
        self.user.save()

    @pytest.mark.django_db
    def test_01(self, client):
        self.init()

        url = '/o/token/'
        dic = {
            'grant_type': 'password',
            'username': self.user.email,
            'password': '111',
            'client_id': self.application.client_id,
            'client_secret': self.application.client_secret
        }
        response = client.post(url, dic)
        assert response.status_code == 200
        rd = response.json()

        token = rd['access_token']

        # Use received token for oauth request.
        url = '/v1/oauth/test'

        # Request without auth - should get error.
        response = client.get(url)
        assert response.status_code == 401

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = client.get(url)

        assert response.status_code == 200

    @pytest.mark.django_db
    def test_02(self, client):
        self.init()
