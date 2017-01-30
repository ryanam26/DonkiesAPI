import pytest
from .. import base
from ..factories import TransactionFactory
from django.conf import settings


class TestTransferUser(base.Mixin):
    @pytest.mark.django_db
    def test(self):
        from finance.models import Transaction
        import datetime
        dt = datetime.date.today() - datetime.timedelta(days=365)

        res = Transaction.objects.get_atrium_transactions(
            'USR-7fb22704-763e-ad5a-487d-f2f8338d068a',
            from_date=dt)
        print(res)
