import pytest
from finance.models import PlaidWebhook
from .import base
from .factories import ItemFactory


class TestPlaidWebhooks(base.Mixin):
    """
    Test model's manager "process_webhook".
    """
    @pytest.mark.django_db
    def test_initial_update(self):
        d = {
            'webhook_type': 'TRANSACTIONS',
            'webhook_code': 'INITIAL_UPDATE',
            'error': None,
            'new_transactions': 19
        }
        item = ItemFactory.get_item()
        d['item_id'] = item.plaid_id
        PlaidWebhook.objects.process_webhook(d)
        assert PlaidWebhook.objects.count() == 1

    @pytest.mark.django_db
    def test_historical_update(self):
        d = {
            'webhook_type': 'TRANSACTIONS',
            'webhook_code': 'HISTORICAL_UPDATE',
            'error': None,
            'new_transactions': 19
        }
        item = ItemFactory.get_item()
        d['item_id'] = item.plaid_id
        PlaidWebhook.objects.process_webhook(d)
        assert PlaidWebhook.objects.count() == 1

    @pytest.mark.django_db
    def test_default_update(self):
        d = {
            'webhook_type': 'TRANSACTIONS',
            'webhook_code': 'DEFAULT_UPDATE',
            'error': None,
            'new_transactions': 19
        }
        item = ItemFactory.get_item()
        d['item_id'] = item.plaid_id
        PlaidWebhook.objects.process_webhook(d)
        assert PlaidWebhook.objects.count() == 1

    @pytest.mark.django_db
    def test_removed_transaction(self):
        d = {
            'webhook_type': 'TRANSACTIONS',
            'webhook_code': 'REMOVED_TRANSACTIONS',
            'error': None,
            'removed_transactions': [
                'yBVBEwrPyJs8GvR77N7QTxnGg6wG74H7dEDN6',
                'kgygNvAVPzSX9KkddNdWHaVGRVex1MHm3k9no'
            ],
        }
        item = ItemFactory.get_item()
        d['item_id'] = item.plaid_id
        PlaidWebhook.objects.process_webhook(d)
        assert PlaidWebhook.objects.count() == 1

    @pytest.mark.django_db
    def test_item_updated(self):
        d = {
            'webhook_type': 'ITEM',
            'webhook_code': 'WEBHOOK_UPDATE_ACKNOWLEDGED',
            'error': None,
        }
        item = ItemFactory.get_item()
        d['item_id'] = item.plaid_id
        PlaidWebhook.objects.process_webhook(d)
        assert PlaidWebhook.objects.count() == 1

    @pytest.mark.django_db
    def test_error(self):
        d = {
            'webhook_type': 'ITEM',
            'webhook_code': 'ERROR',
            'error': {
                'display_message': 'Some message',
                'error_code': 'ITEM_LOGIN_REQUIRED',
                'error_message': 'the provided credentials were not correct',
                'error_type': 'ITEM_ERROR',
                'status': 400
            }
        }
        item = ItemFactory.get_item()
        d['item_id'] = item.plaid_id
        PlaidWebhook.objects.process_webhook(d)
        assert PlaidWebhook.objects.count() == 1
