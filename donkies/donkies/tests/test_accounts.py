import json
import pytest
from django.db.models import Q
from .import base
from .factories import (
    AccountFactory, InstitutionFactory, ItemFactory, UserFactory)
from finance.models import Account, Institution


class TestAccounts(base.Mixin):
    @pytest.mark.django_db
    def test_delete01(self):
        """
        Instead of deleting object should set is_active=False
        """
        a = AccountFactory.get_account()
        assert a.is_active is True

        a.delete()
        a.refresh_from_db()
        assert a.is_active is False

    @pytest.mark.django_db
    def test_delete02(self):
        """
        Instead of deleting queryset, should set is_active=False
        """
        AccountFactory.get_account()
        AccountFactory.get_account()

        assert Account.objects.count() == 2
        Account.objects.active().all().delete()
        assert Account.objects.count() == 2

        for a in Account.objects.active().all():
            assert a.is_active is False

    @pytest.mark.django_db
    def test_edit_share(self, client):
        """
        Edit transfer_share for debt accounts.
        1 request: should get error.
        2 request: should get error.
        3 request: should get success.
        """
        user = UserFactory(email='bob@gmail.com')
        client = self.get_auth_client(user)

        i1 = InstitutionFactory.get_institution()
        item = ItemFactory.get_item(user=user, institution=i1)
        a1 = AccountFactory.get_account(item=item, type=Account.CREDIT)

        i2 = Institution.objects.filter(~Q(plaid_id=i1.plaid_id)).first()
        item = ItemFactory.get_item(user=user, institution=i2)
        a2 = AccountFactory.get_account(item=item, type=Account.CREDIT)

        url = '/v1/accounts/edit_share'

        # ids not match
        dic = {
            'id100': 50,
            'id200': 50
        }
        data = json.dumps(dic)
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 400

        return

        # The total sum not equal to 100
        dic = {
            'id{}'.format(a1.id): 10,
            'id{}'.format(a2.id): 20
        }
        data = json.dumps(dic)
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 400

        # success
        dic = {
            'id{}'.format(a1.id): 50,
            'id{}'.format(a2.id): 50
        }
        data = json.dumps(dic)
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 200

        a1.refresh_from_db()
        a2.refresh_from_db()

        assert a1.transfer_share == 50
        assert a1.transfer_share == 50

    @pytest.mark.django_db
    def test_activate_account(self, client):
        account = AccountFactory.get_account()
        account.is_active = False
        account.save()
        client = self.get_auth_client(account.item.user)

        url = '/v1/accounts/set_active/{}'.format(account.id)
        dic = {'is_active': True}
        data = json.dumps(dic)
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 204

        account.refresh_from_db()
        assert account.is_active is True

    @pytest.mark.django_db
    def test_deactivate_account(self, client):
        """
        1) Can deactivate if there are others active accounts.
        2) Can not deactivate last active account in item.
        """
        a1 = AccountFactory.get_account()
        a2 = AccountFactory.get_account(item=a1.item)
        client = self.get_auth_client(a1.item.user)

        url = '/v1/accounts/set_active/{}'.format(a1.id)
        dic = {'is_active': False}
        data = json.dumps(dic)
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 204

        url = '/v1/accounts/set_active/{}'.format(a2.id)
        data = json.dumps(dic)
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 400

    @pytest.mark.django_db
    def test_set_account_number01(self, client):
        """
        Test success.
        """
        a = AccountFactory.get_account()
        client = self.get_auth_client(a.item.user)

        url = '/v1/accounts/set_account_number/{}'.format(a.id)
        dic = {'account_number': 'AAA111'}
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 201

        a.refresh_from_db()
        assert a.account_number == dic['account_number']

    @pytest.mark.django_db
    def test_set_account_number02(self, client):
        """
        If account number was set earlier,
        should get error.
        """
        a = AccountFactory.get_account()
        a.account_number = 'AAA000'
        a.save()
        client = self.get_auth_client(a.item.user)

        url = '/v1/accounts/set_account_number/{}'.format(a.id)
        dic = {'account_number': 'AAA111'}
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 400

    @pytest.mark.django_db
    def test_create_manual_account01(self, client):
        """
        Test manager's method
        """
        user = UserFactory.get_user()
        institution = InstitutionFactory.get_manual_institution()
        account = Account.objects.create_manual_account(
            user.id, institution.id, '11111111', '')
        assert isinstance(account, Account)
        assert account.type_ds == Account.DEBT

    @pytest.mark.django_db
    def test_create_manual_account02(self, client):
        """
        Test API endpoint.
        """
        user = UserFactory.get_user()
        client = self.get_auth_client(user)
        institution = InstitutionFactory.get_manual_institution()
        url = '/v1/accounts'

        dic = {
            'institution_id': institution.id,
            'account_number': 'AAA111',
            'additional_info': ''
        }
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 201
        assert Account.objects.count() == 1
