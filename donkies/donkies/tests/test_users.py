import datetime
import json
import pytest
from faker import Faker
from django.contrib import auth
from donkies.tests.services.emulator import Emulator
from web.management.commands.createemails import Command
from web.models import User, Emailer, ChangeEmailHistory
from finance.models import (
    Member, Account, Transaction, TransferDonkies, TransferUser)
from .factories import UserFactory, AccountFactory, MemberFactory
from .import base


class TestUsers(base.Mixin):
    def init_emailer(self):
        cmd = Command()
        cmd.create_change_email()
        cmd.create_reset_password()
        cmd.create_signup()
        cmd.create_resend_reg_confirmation()

    @pytest.mark.django_db
    def notest_get(self, client):
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
    def notest_edit(self, client):
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
    def notest_change_password01(self, client):
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
    def notest_change_password02(self, client):
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
    def notest_change_password03(self, client):
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
    def notest_change_password04(self, client):
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
    def notest_change_email01(self, client):
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
    def notest_change_email02(self, client):
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
    def notest_resend_confirmation(self, client):
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

    @pytest.mark.django_db
    def notest_edit_settings(self, client):
        """
        Test edit user settings.
        Should get success.
        """
        user = UserFactory(email='bob@gmail.com')
        user.minimum_transfer_amount = 5
        user.save()

        client = self.get_auth_client(user)

        url = '/v1/user_settings'
        dic = {
            'minimum_transfer_amount': 100,
        }

        data = json.dumps(dic)
        response = client.patch(url, data, content_type='application/json')
        assert response.status_code == 200

        user.refresh_from_db()
        assert user.minimum_transfer_amount == 100

    @pytest.mark.django_db
    def notest_password_reset_request01(self, client):
        """
        Should get success.
        Emailer should have email with reset_token.
        """
        self.init_emailer()
        user = UserFactory(email='bob@gmail.com')
        client = self.get_auth_client(user)

        url = '/v1/password/reset/request'
        dic = {
            'email': 'bob@gmail.com',
        }
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 204

        em = Emailer.objects.first()
        assert user.encrypted_id in em.txt
        assert user.reset_token in em.txt

    @pytest.mark.django_db
    def notest_password_reset_request02(self, client):
        """
        Test with non existing email.
        Should get error.
        """
        self.init_emailer()
        user = UserFactory(email='bob@gmail.com')
        client = self.get_auth_client(user)

        url = '/v1/password/reset/request'
        dic = {
            'email': 'incorrect@gmail.com',
        }
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 400

    @pytest.mark.django_db
    def notest_password_reset01(self, client):
        """
        Should get success.
        """
        self.init_emailer()
        user = UserFactory(email='bob@gmail.com')
        client = self.get_auth_client(user)

        user.reset_request()

        url = '/v1/password/reset'
        dic = {
            'encrypted_id': user.encrypted_id,
            'reset_token': user.reset_token,
            'new_password': '12345678'
        }
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 204

        user = auth.authenticate(email=user.email, password='12345678')
        assert user is not None
        assert user.reset_token == ''
        assert user.reset_at is None

    @pytest.mark.django_db
    def notest_password_reset02(self, client):
        """
        Test with small password.
        The password should be at least 8 symbols.
        Should get error.
        """
        self.init_emailer()
        user = UserFactory(email='bob@gmail.com')
        client = self.get_auth_client(user)

        user.reset_request()

        url = '/v1/password/reset'
        dic = {
            'encrypted_id': user.encrypted_id,
            'reset_token': user.reset_token,
            'new_password': '111'
        }
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 400

    @pytest.mark.django_db
    def notest_password_reset03(self, client):
        """
        Test with incorrect encrypted_id.
        Should get error.
        """
        self.init_emailer()
        user = UserFactory(email='bob@gmail.com')
        client = self.get_auth_client(user)

        user.reset_request()

        url = '/v1/password/reset'
        dic = {
            'encrypted_id': 'incorrect',
            'reset_token': user.reset_token,
            'new_password': '12345678'
        }
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 400

    @pytest.mark.django_db
    def notest_password_reset04(self, client):
        """
        Test with incorrect reset_token.
        Should get error.
        """
        self.init_emailer()
        user = UserFactory(email='bob@gmail.com')
        client = self.get_auth_client(user)

        user.reset_request()

        url = '/v1/password/reset'
        dic = {
            'encrypted_id': user.encrypted_id,
            'reset_token': 'incorrect',
            'new_password': '12345678'
        }
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 400

    @pytest.mark.django_db
    def notest_total_debt(self, client):
        user = UserFactory(email='bob@gmail.com')
        assert user.total_debt == 0

        m = MemberFactory.get_member(user=user)
        a1 = AccountFactory.get_account(member=m, type=Account.LOAN)
        a2 = AccountFactory.get_account(member=m, type=Account.LOAN)

        a1.balance = 100
        a2.balance = 100
        a1.save()
        a2.save()

        user.refresh_from_db()
        assert user.total_debt == 200

    @pytest.mark.django_db
    def test_close_account(self):
        """
        User closes Donkies account.
        All required steps listed in "user.close_account" method.
        """
        e = Emulator()
        e.init()

        # Emulate transfers to Dwolla
        e.create_dwolla_transfers(30)
        count = TransferDonkies.objects.filter(is_sent=True).count()
        assert count > 0

        count = TransferDonkies.objects.filter(
            is_processed_to_user=True).count()
        assert count == 0

        count = TransferUser.objects.all().count()
        assert count == 0

        # Close user's account
        e.user.close_account(is_delete_atrium=False)

        # All user's members, accounts and transactions should
        # be not active
        assert Member.objects.filter(is_active=True).count() == 0
        assert Account.objects.filter(is_active=True).count() == 0
        assert Transaction.objects.filter(is_active=True).count() == 0

        # All transfers from TransferDonkies should be processed.
        count = TransferDonkies.objects.filter(
            is_processed_to_user=False).count()
        assert count == 0

        count = TransferDonkies.objects.filter(
            is_processed_to_user=True).count()
        assert count > 0

        # TransferUser model should be filled
        count = TransferUser.objects.all().count()
        assert count > 0
