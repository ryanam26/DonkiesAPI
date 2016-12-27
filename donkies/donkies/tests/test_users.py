import datetime
import json
import pytest
from faker import Faker
from web.management.commands.createemails import Command
from web.models import User, Emailer, ChangeEmailHistory
from .factories import UserFactory
from .import base


class TestUsers(base.Mixin):
    def init_emailer(self):
        cmd = Command()
        cmd.create_change_email()
        cmd.create_reset_password()
        cmd.create_signup()
        cmd.create_resend_reg_confirmation()

    @pytest.mark.django_db
    def test_get(self, client):
        """
        Test user get.
        """
        user = UserFactory(email='bob@gmail.com')
        client = self.get_auth_client(user)

        url = '/v1/user'
        response = client.get(url)
        assert response.status_code == 200

        rd = response.json()
        assert user.email == rd['email']

    @pytest.mark.django_db
    def test_edit(self, client):
        """
        Test user get.
        """
        user = UserFactory(email='bob@gmail.com')
        client = self.get_auth_client(user)

        url = '/v1/user'
        dic = {
            'first_name': 'John',
            'last_name': 'Johnson',
            'address1': 'new address1',
            'address2': 'new address2',
            'city': Faker().city(),
            'state': 'AL',
            'postal_code': Faker().postalcode(),
            'date_of_birth': '1979-09-09',
            'ssn': Faker().ssn()

        }

        data = json.dumps(dic)
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 200

        user = User.objects.get(email=user.email)
        for key, value in dic.items():
            db_value = getattr(user, key)
            if isinstance(db_value, datetime.date):
                assert value == db_value.strftime('%Y-%m-%d')
            else:
                assert value == db_value

    @pytest.mark.django_db
    def test_change_password01(self, client):
        """
        Min lenght should equal 8 symbols.
        Should get error.
        """
        user = UserFactory(email='bob@gmail.com', first_name='bob')

        client = self.get_auth_client(user)
        url = '/v1/user/change/password'
        dic = {
            'current_password': 'wrong',
            'new_password1': '111',
            'new_password2': '111',
        }
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 400

    @pytest.mark.django_db
    def test_change_password02(self, client):
        """
        Test with different passwords.
        Should get error.
        """
        user = UserFactory(email='bob@gmail.com', first_name='bob')
        user.set_password('111')
        user.save()

        client = self.get_auth_client(user)
        url = '/v1/user/change/password'
        dic = {
            'current_password': '111',
            'new_password1': '11111111',
            'new_password2': '22222222',
        }
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 400

    @pytest.mark.django_db
    def test_change_password03(self, client):
        """
        Test with incorrect current password.
        Should get error.
        """
        user = UserFactory(email='bob@gmail.com', first_name='bob')

        client = self.get_auth_client(user)
        url = '/v1/user/change/password'
        dic = {
            'current_password': 'wrong',
            'new_password1': '11111111',
            'new_password2': '11111111',
        }
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 400

    @pytest.mark.django_db
    def test_change_password04(self, client):
        """
        Test with correct data.
        """
        user = UserFactory(email='bob@gmail.com', first_name='bob')
        user.set_password('11111111')
        user.save()

        client = self.get_auth_client(user)
        url = '/v1/user/change/password'
        dic = {
            'current_password': '11111111',
            'new_password1': '22222222',
            'new_password2': '22222222',
        }
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_change_email01(self, client):
        """
        Submit wrong email. Should get error.
        """
        user = UserFactory(email='bob@gmail.com', first_name='bob')
        client = self.get_auth_client(user)
        url = '/v1/user/change/email'
        dic = {'new_email': 'incorrect'}
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 400

    @pytest.mark.django_db
    def test_change_email02(self, client):
        """
        1) user.new_email = new_email
        2) user.new_email_token = generated
        3) user.new_email_expire_at= '+ 1 hour'
        4) send user email with confirmation link.
        5) confirmation
        6) check email history
        """
        self.init_emailer()
        user = UserFactory(email='bob@gmail.com', first_name='bob')
        client = self.get_auth_client(user)
        url = '/v1/user/change/email'
        dic1 = {'new_email': 'bobby@gmail.com'}
        data = json.dumps(dic1)
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 200

        user.refresh_from_db()
        assert user.new_email == dic1['new_email']
        assert user.new_email_token is not None
        assert user.new_email_expire_at is not None

        em = Emailer.objects.first()
        assert user.encrypted_id in em.txt
        assert user.new_email_token in em.txt

        # test confirmation
        url = '/v1/user/change/email/confirm/{}/{}'.format(
            user.encrypted_id, user.new_email_token)
        dic2 = {}
        data = json.dumps(dic2)
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 200

        user.refresh_from_db()
        assert user.email == dic1['new_email']

        ceh = ChangeEmailHistory.objects.first()
        assert ceh.email_new == dic1['new_email']

    @pytest.mark.django_db
    def test_resend_confirmation(self, client):
        """
        If user didn't receive reg email, it can request to resend
        confirmation email.
        """
        self.init_emailer()
        user = UserFactory(email='bob@gmail.com', first_name='bob')
        user.is_confirmed = False
        user.save()
        client = self.get_auth_client(user)

        count = user.confirmation_resend_count

        url = '/v1/user/resend_reg_confirmation_link'
        response = client.get(url, content_type='application/json')
        assert response.status_code == 200

        user.refresh_from_db()
        em = Emailer.objects.first()

        assert user.get_confirmation_link() in em.txt.replace('&amp;', '&')
        assert user.confirmation_resend_count == count + 1

        user.is_confirmed = True
        user.save()

        url = '/v1/user/resend_reg_confirmation_link'
        response = client.get(url, content_type='application/json')
        assert response.status_code == 200
