import pytest
from .. import base
from ..factories import TransactionFactory
from django.conf import settings


class TestTransferUser(base.Mixin):
    @pytest.mark.django_db
    def test(self):
        """
        Temp test for Atrium
        """
        settings.ATRIUM_API_MODE = 'PROD'

        from finance.services.atrium_api import AtriumApi
        a = AtriumApi()
        res = a.search_institutions()
        print(res)
