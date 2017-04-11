import json
import pytest
from donkies.tests.services.dwolla.emulator import Emulator
from bank.models import FundingSource, FundingSourceIAVLog

from ...factories import AccountFactory
from ...import base


class TestFundingSource(base.Mixin):
    @pytest.mark.django_db
    def test_create_manual(self, client):
        """
        Manual creation using account_number and routing_number.
        Test API endpoint for creating funding source.
        """
        account = AccountFactory.get_account()
        client = self.get_auth_client(account.item.user)

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
        account = AccountFactory.get_account()
        dwolla_id = 'some-id'

        e = Emulator()
        test_dic = e.get_funding_source_dic(dwolla_id)

        fs = FundingSource.objects.create_funding_source_iav(
            account.id, dwolla_id, test_dic)

        assert fs.dwolla_id == test_dic['id']

        fs_log = FundingSourceIAVLog.objects.get(dwolla_id=test_dic['id'])
        assert fs_log.is_processed is True
