import json
import pytest
from finance.services.plaid_api import PlaidApi
from finance.models import Institution
from .import base
from .factories import (
    AccountFactory, InstitutionFactory, MemberFactory, UserFactory)


class TestPlaid(base.Mixin):
    USERNAME = 'user_good'
    PASSWORD_GOOD = 'pass_good'

    @pytest.mark.django_db
    def notest_create_institution(self):
        """
        Test model's manager.
        If institution does not exist in database, query it from API.
        """
        plaid_id = 'ins_109508'
        i = Institution.objects.get_or_create_institution(plaid_id)
        assert isinstance(i, Institution)
        assert Institution.objects.count() == 1

    @pytest.mark.django_db
    def test_create_item01(self):
        i = InstitutionFactory.get_institution()
        pa = PlaidApi()
        item = pa.create_item(
            self.USERNAME, self.PASSWORD_GOOD, i.plaid_id)
        print(item)
