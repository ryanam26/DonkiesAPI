import calendar
import datetime
import pytest
from rest_framework.test import APIClient
from django.conf import settings
from finance.services.plaid_api import PlaidApi
from web.models import User
from .factories import ItemFactory


class Mixin:
    @pytest.mark.django_db
    def setup(self):
        """
        The data available for all fake tests.
        """
        pass

    @pytest.mark.django_db
    def login(self):
        user = User.objects.get(user__email=self.email)
        token = user.get_token()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def get_auth_client(self, user):
        client = APIClient()
        user = User.objects.get(id=user.id)
        token = user.get_token()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        return client

    def get_access_token(self):
        """
        In order to not create access_token each time,
        store in Redis.
        Returns (access_token, plaid_account_id)
        """
        pa = PlaidApi()
        rs = settings.REDIS_DB

        access_token = rs.get('access_token')
        if access_token is None:
            item = ItemFactory.get_plaid_item()
            access_token = item.access_token
            rs.set('access_token', access_token)

            res = pa.get_accounts(access_token)
            accounts = res['accounts']
            accounts = [acc for acc in accounts if acc['type'] == 'depository']
            acc = accounts[0]
            rs.set('account_id', acc['account_id'])

        access_token = rs.get('access_token').decode()
        account_id = rs.get('account_id').decode()
        return access_token, account_id

    def get_last_date_of_the_month(self):
        dt = datetime.date.today()
        _, last = calendar.monthrange(dt.year, dt.month)
        dt = dt.replace(day=last)
        return dt
