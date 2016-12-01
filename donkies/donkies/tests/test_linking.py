import json
import pytest
from .import base
from finance.models import Account, LinkDebt
from .factories import (
    AccountFactory, InstitutionFactory, MemberFactory, UserFactory)
from finance.services.transfer import TransferService


class TestLinking(base.Mixin):
    def get_account(self, code):
        user = UserFactory(email='bob@gmail.com')
        i = InstitutionFactory(code=code)
        m = MemberFactory(user=user, institution=i)
        return AccountFactory(member=m, type=Account.LOAN)

    @pytest.mark.django_db
    def test_share(self, client):
        a1 = self.get_account('code1')
        a2 = self.get_account('code2')
        a3 = self.get_account('code3')
        a4 = self.get_account('code4')

        # Create 1st link
        # Share should be equal 100%,
        # doesn't matter what share pass to function.
        ld1 = LinkDebt.objects.create_link(a1, 55)
        assert ld1.share == 100

        # Create 2nd link with share 30%
        # Should get: link1 = 70%, link2 = 30%
        ld2 = LinkDebt.objects.create_link(a2, 30)
        ld1.refresh_from_db()
        ld2.refresh_from_db()
        assert ld1.share == 70
        assert ld2.share == 30

        # Create 3rd link with share 40%
        # Should get: link1 = 50%, link2 = 10%, link3 = 40%
        ld3 = LinkDebt.objects.create_link(a3, 40)
        ld1.refresh_from_db()
        ld2.refresh_from_db()
        ld3.refresh_from_db()
        assert ld1.share == 50
        assert ld2.share == 10
        assert ld3.share == 40

        # Create 4th link with share 60%
        # Should get: link1 = 25%, link2 = 0%, link3 = 15%, link4=60%
        ld4 = LinkDebt.objects.create_link(a4, 60)
        ld1.refresh_from_db()
        ld2.refresh_from_db()
        ld3.refresh_from_db()
        ld4.refresh_from_db()
        assert ld1.share == 25
        assert ld2.share == 0
        assert ld3.share == 15
        assert ld4.share == 60

    @pytest.mark.django_db
    def test_transfer(self, client):
        t = TransferService(
            TransferService.mock_transactions(),
            TransferService.mock_accounts())
        t.run()

    @pytest.mark.django_db
    def test_link_debt_get(self, client):
        a1 = self.get_account('code1')
        a2 = self.get_account('code2')
        a3 = self.get_account('code3')
        client = self.get_auth_client(a3.member.user)

        LinkDebt.objects.create_link(a1, 60)
        LinkDebt.objects.create_link(a2, 20)
        LinkDebt.objects.create_link(a3, 20)

        url = '/v1/link_debts'
        response = client.get(url)
        rd = response.json()
        assert response.status_code == 200
        assert len(rd) == 3

    @pytest.mark.django_db
    def test_link_debt_create01(self, client):
        """
        Create link with share more than 100%.
        Should get error.
        """

        account = self.get_account('code')
        client = self.get_auth_client(account.member.user)

        url = '/v1/link_debts'
        dic = {
            'account': account.id,
            'share': 101
        }
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 400

    @pytest.mark.django_db
    def test_link_debt_create02(self, client):
        """
        Create link with not debt account.
        Should get error.
        """
        account = self.get_account('code')
        account.type_ds = Account.DEBIT
        account.save()

        client = self.get_auth_client(account.member.user)

        url = '/v1/link_debts'
        dic = {
            'account': account.id,
            'share': 20
        }
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 400

    @pytest.mark.django_db
    def test_link_debt_create03(self, client):
        """
        Should get success.
        """
        account = self.get_account('code')
        client = self.get_auth_client(account.member.user)

        url = '/v1/link_debts'
        dic = {
            'account': account.id,
            'share': 20
        }
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 201
