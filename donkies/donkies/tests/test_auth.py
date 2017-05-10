import json
import pytest
from django.contrib import auth
from web.models import User, Email, Emailer
from .factories import UserFactory, EmailFactory
from .import base


class TestAuth(base.Mixin):
    """
    Tests for signup, signup confirm, login, password reset.
    """
    def init(self):
        """
        Each group contains 2 users.
        Each subscription contains 2 groups and 1 user (total 5 users.)
        """
        dic = {
            'txt': '{{ user.get_confirmation_link }}',
            'html': '{{ user.get_confirmation_link }}'
        }
        EmailFactory(code=Email.SIGNUP, name='EE', **dic)

        dic = {
            'txt': '{{ user.get_reset_link }}',
            'html': '{{ user.get_reset_link }}'
        }
        EmailFactory(code=Email.RESET_PASSWORD, name='EE', **dic)

    def print_emailer(self):
        for em in Emailer.objects.all():
            print('-------')
            print('email_to: {}'.format(em.email_to))
            print('email_from: {}'.format(em.email_from))
            print('subject: {}'.format(em.subject))
            print('txt: {}'.format(em.txt))

    @pytest.mark.django_db
    def test_signup01(self, client):
        """
        Test with correct email.
        User should get email with confirmation link.
        """
        self.init()
        url = '/v1/auth/signup'
        dic = {
            'email': 'bob@gmail.com',
            'password': '12345678',
            'first_name': 'Bob',
            'last_name': 'Smith'
        }
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 204

        user = UserFactory(email='bob@gmail.com')
        assert user.email == 'bob@gmail.com'

        em = Emailer.objects.first()
        assert em is not None
        # self.print_emailer()

    @pytest.mark.django_db
    def test_signup02(self, client):
        """
        Test with incorrect email.
        """
        self.init()
        url = '/v1/auth/signup'
        dic = {
            'email': '!!!',
            'password': '12345678',
            'first_name': 'Bob',
            'last_name': 'Smith'
        }
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        # print(response.content)
        assert response.status_code == 400

    @pytest.mark.django_db
    def test_signup03(self, client):
        """
        Test with empty email.
        """
        self.init()
        url = '/v1/auth/signup'
        dic = {
            'email': '',
            'password': '12345678',
            'first_name': 'Bob',
            'last_name': 'Smith'
        }
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        # print(response.content)
        assert response.status_code == 400

    @pytest.mark.django_db
    def test_signup04(self, client):
        """
        Test with empty password.
        """
        self.init()
        url = '/v1/auth/signup'
        dic = {
            'email': 'bob@gmail.com',
            'password': '',
            'first_name': 'Bob',
            'last_name': 'Smith'
        }
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        # print(response.content)
        assert response.status_code == 400

    @pytest.mark.django_db
    def test_signup05(self, client):
        """
        Test with taken email.
        """
        self.init()
        UserFactory(email='bob@gmail.com')

        url = '/v1/auth/signup'
        dic = {
            'email': 'bob@gmail.com',
            'password': '12345678',
            'first_name': 'Bob',
            'last_name': 'Smith'
        }
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        # print(response.content)
        assert response.status_code == 400

    @pytest.mark.django_db
    def test_signup06(self, client):
        """
        Test with small password.
        The minimum password length should be at least 8 symbols.
        """
        self.init()
        url = '/v1/auth/signup'
        dic = {
            'email': 'bob@gmail.com',
            'password': '111',
            'first_name': 'Bob',
            'last_name': 'Smith'
        }
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 400

    @pytest.mark.django_db
    def test_signup_confirm01(self, client):
        """
        Test with correct data.
        """
        self.init()
        url = '/v1/auth/signup/confirm'
        user = UserFactory(email='bob@gmail.com')
        user.is_confirmed = False
        user.save()
        data = {
            'encrypted_id': user.encrypted_id,
            'confirmation_token': user.confirmation_token
        }

        response = client.post(url, data)
        assert response.status_code == 201

        d = response.json()
        assert user.get_token().key == d['token']

        user = UserFactory(email='bob@gmail.com')
        assert user.is_confirmed is True
        assert user.confirmed_at is not None

    @pytest.mark.django_db
    def test_signup_confirm02(self, client):
        """
        Test with incorrect data.
        """
        url = '/v1/auth/signup/confirm'
        data = {
            'encrypted_id': 'aaa',
            'confirmation_token': 'bbb'
        }
        response = client.post(url, data)
        assert response.status_code == 400

    @pytest.mark.django_db
    def test_login01(self, client):
        """
        Test with correct data.
        """
        user = UserFactory(email='bob@gmail.com')
        user.set_password('111')
        user.save()

        url = '/v1/auth/login'
        data = {
            'email': user.email,
            'password': '111'
        }

        response = client.post(url, data)
        assert response.status_code == 200

        d = response.json()
        user = User.objects.get(id=user.id)
        assert user.get_token().key == d['token']

    @pytest.mark.django_db
    def test_login02(self, client):
        """
        Test with empty email.
        """
        user = UserFactory(email='bob@gmail.com')
        user.set_password('111')
        user.save()

        url = '/v1/auth/login'
        data = {
            'email': '',
            'password': '111'
        }

        response = client.post(url, data)
        assert response.status_code == 400

    @pytest.mark.django_db
    def test_login03(self, client):
        """
        Test with empty password.
        """
        user = UserFactory(email='bob@gmail.com')
        user.set_password('111')
        user.save()

        url = '/v1/auth/login'
        data = {
            'email': user.email,
            'password': ''
        }

        response = client.post(url, data)
        assert response.status_code == 400

    @pytest.mark.django_db
    def test_login05(self, client):
        """
        Test with not existing email.
        """
        user = UserFactory(email='bob@gmail.com')
        user.set_password('111')
        user.save()

        url = '/v1/auth/login'
        data = {
            'email': 'az@az.com',
            'password': '111'
        }

        response = client.post(url, data)
        assert response.status_code == 400

    @pytest.mark.django_db
    def test_login06(self, client):
        """
        Test with incorrect password.
        """
        user = UserFactory(email='bob@gmail.com')
        user.set_password('111')
        user.save()

        url = '/v1/auth/login'
        data = {
            'email': user.email,
            'password': '555'
        }

        response = client.post(url, data)
        assert response.status_code == 400

    @pytest.mark.django_db
    def test_login07(self, client):
        """
        User can't login if is_active=False
        """
        user = UserFactory(email='bob@gmail.com')
        user.set_password('111')
        user.is_active = False
        user.save()

        url = '/v1/auth/login'
        data = {
            'email': user.email,
            'password': '111'
        }

        response = client.post(url, data)
        assert response.status_code == 400

    @pytest.mark.django_db
    def test_login08(self, client):
        """
        User can login if is_confirmed=False
        The restriction logic after login is on frontend.
        """
        user = UserFactory(email='bob@gmail.com')
        user.set_password('111')
        user.is_confirmed = False
        user.save()

        url = '/v1/auth/login'
        data = {
            'email': user.email,
            'password': '111'
        }

        response = client.post(url, data)
        assert response.status_code == 200
