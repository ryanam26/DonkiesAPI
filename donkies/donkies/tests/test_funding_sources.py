import json
import pytest
from .import base
from .emulator import Emulator
from .factories import (
    AccountFactory, InstitutionFactory, MemberFactory, UserFactory)
from bank.models import FundingSource, FundingSourceIAVLog
from finance.models import Account


class TestFundingSource(base.Mixin):
    def get_account(self, code):
        user = UserFactory(email='bob@gmail.com')
        i = InstitutionFactory(code=code)
        m = MemberFactory(user=user, institution=i)
        return AccountFactory(member=m, type=Account.SAVINGS)

    @pytest.mark.django_db
    def test_create_manual(self, client):
        """
        Manual creation using account_number and routing_number.
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

    @pytest.mark.django_db
    def test_create_iav(self, client):
        """
        Test when funding source is created
        by IAV from frontend.
        """
        account = self.get_account('mxbank')
        dwolla_id = 'some-id'

        e = Emulator()
        test_dic = e.get_funding_source_dic(dwolla_id)

        fs = FundingSource.objects.create_funding_source_iav(
            account.id, dwolla_id, test_dic)

        assert fs.dwolla_id == test_dic['id']

        fs_log = FundingSourceIAVLog.objects.get(dwolla_id=test_dic['id'])
        assert fs_log.is_processed is True
