import pytest
from .import base
from .factories import (
    AccountFactory, InstitutionFactory, MemberFactory, UserFactory)
from finance.models import Member


class TestAccounts(base.Mixin):
    @pytest.mark.django_db
    def test_delete_account01(self, client):
        """
        Test post_delete signal.
        When delete account, check if member connected
        only to this account and delete member also.
        """
        user = UserFactory(email='bob@gmail.com')

        i = InstitutionFactory(code='mxbank')
        m = MemberFactory(user=user, institution=i)
        a = AccountFactory(member=m)

        a.delete()

        qs = Member.objects.filter(id=m.id)
        assert qs.count() == 0

    @pytest.mark.django_db
    def test_delete_account02(self, client):
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
    def test_delete_account03(self, client):
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
    def test_delete_account04(self, client):
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
