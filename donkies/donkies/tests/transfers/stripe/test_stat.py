import pytest
from donkies.tests.services.stripe.emulator import Emulator
from ach.models import TransferUser, TransferDebt
from finance.models import Stat
from donkies.tests import base


class TestStat(base.Mixin):
    @pytest.mark.django_db
    def test_01(self):
        """
        Test Stat model manager's method.
        """
        e = Emulator()
        e.init()
        e.create_stripe_transfers(90)

        TransferUser.objects.process_users()
        assert TransferUser.objects.count() > 0
        assert TransferDebt.objects.count() > 0

        print(Stat.objects.get_json(e.user.id))
