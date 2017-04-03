import json
import pytest
from finance.services.plaid_api import PlaidApi
from finance.models import Account
from .import base
from .factories import (
    AccountFactory, InstitutionFactory, MemberFactory, UserFactory)


class TestPlaid(base.Mixin):
    USERNAME = 'user_good'
    PASSWORD_GOOD = 'pass_good'

    @pytest.mark.django_db
    def test_create_item01(self):
        """
        """
        i = InstitutionFactory.get_institution()
        pa = PlaidApi()
        item = pa.create_item(
            self.USERNAME, self.PASSWORD_GOOD, i.plaid_id)
        print(item)