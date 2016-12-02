import json
import pytest
from .import base
from .factories import (
    AccountFactory, InstitutionFactory, MemberFactory, UserFactory)
from bank.models import FundingSource
from finance.models import Account


class TestFundingSource(base.Mixin):
    def get_account(self, code):
        user = UserFactory(email='bob@gmail.com')
        i = InstitutionFactory(code=code)
        m = MemberFactory(user=user, institution=i)
        return AccountFactory(member=m, type=Account.SAVINGS)

    @pytest.mark.django_db
    def test_create(self, client):
        """
        Test API endpoint for creating funding source.
        """
        account = self.get_account('mxbank')
        client = self.get_auth_client(account.member.user)

        url = '/v1/funding_sources'
        dic = {
            'account_id': account.id,
            'account_number': '1111111111',
            'routing_number': '2222222222',
            'type': FundingSource.SAVINGS,
            'name': 'Some name'
        }
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 201
