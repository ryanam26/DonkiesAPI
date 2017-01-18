import json
import pytest
from .import base
from .factories import (
    AccountFactory, InstitutionFactory, MemberFactory, UserFactory)
from finance.models import Account


class TestAccounts(base.Mixin):
    @pytest.mark.django_db
    def test_delete_account01(self, client):
        """
        Should get success.
        """
        user = UserFactory(email='bob@gmail.com')
        client = self.get_auth_client(user)

        i = InstitutionFactory(code='mxbank')
        m = MemberFactory(user=user, institution=i)
        a = AccountFactory(member=m)

        url = '/v1/accounts/{}'.format(a.id)
        response = client.delete(url)
        assert response.status_code == 204

    @pytest.mark.django_db
    def test_delete_account02(self, client):
        """
        Try to delete non-existing account.
        Should get error.
        """
        user = UserFactory(email='bob@gmail.com')
        client = self.get_auth_client(user)

        url = '/v1/accounts/1000'
        response = client.delete(url)
        assert response.status_code == 404

    @pytest.mark.django_db
    def test_delete_account03(self, client):
        """
        Try to delete account that belongs to other user.
        Should get error.
        """
        user = UserFactory(email='bob@gmail.com')
        i = InstitutionFactory(code='mxbank')
        m = MemberFactory(user=user, institution=i)
        a = AccountFactory(member=m)

        user2 = UserFactory(email='john@gmail.com')
        client = self.get_auth_client(user2)

        url = '/v1/accounts/{}'.format(a.id)
        response = client.delete(url)
        assert response.status_code == 404

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

        i = InstitutionFactory(code='mxbank')
        m = MemberFactory(user=user, institution=i)
        a1 = AccountFactory(member=m, type=Account.LOAN)

        i = InstitutionFactory(code='someother')
        m = MemberFactory(user=user, institution=i)
        a2 = AccountFactory(member=m, type=Account.LOAN)

        url = '/v1/accounts/edit_share'

        # ids not match
        dic = {
            'id100': 50,
            'id200': 50
        }
        data = json.dumps(dic)
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 400

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
