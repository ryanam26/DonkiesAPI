import pytest
from .. import base
from donkies.tests.services.emulator import Emulator
from finance.models import TransferDonkies, TransferUser


class TestTransferUser(base.Mixin):
    @pytest.mark.django_db
    def test_process_to_model01(self):
        """
        Test 3 debt accounts with share: 33%, 33% and 34%
        """
        e = Emulator(num_debt_accounts=3)
        e.init()
        e.run_transfer_prepare()
        e.run_transfer_donkies_prepare()

        Emulator.emulate_dwolla_transfers()

        a = e.debt_accounts[0]
        a.transfer_share = 33
        a.save()

        a = e.debt_accounts[1]
        a.transfer_share = 33
        a.save()

        a = e.debt_accounts[2]
        a.transfer_share = 34
        a.save()

        assert TransferUser.objects.count() == 0
        TransferUser.objects.process_to_model()
        assert TransferUser.objects.count() == 3
        qs = TransferDonkies.objects.filter(is_processed_to_user=False)
        assert qs.count() == 0

    @pytest.mark.django_db
    def test_process_to_model02(self):
        """
        Test 2 debt accounts with share 99% and 1%
        """
        e = Emulator(num_debt_accounts=2)
        e.init()
        e.run_transfer_prepare()
        e.run_transfer_donkies_prepare()

        Emulator.emulate_dwolla_transfers()

        a = e.debt_accounts[0]
        a.transfer_share = 99
        a.save()

        a = e.debt_accounts[1]
        a.transfer_share = 1
        a.save()

        TransferUser.objects.process_to_model()
        assert TransferUser.objects.count() == 2
        qs = TransferDonkies.objects.filter(is_processed_to_user=False)
        assert qs.count() == 0

    @pytest.mark.django_db
    def test_process_to_model03(self):
        """
        Test 2 debts accounts with share: 100% and 0%
        TransferUser model should get only 1 item instead of 2.
        """

        e = Emulator()
        e.init()
        e.run_transfer_prepare()
        e.run_transfer_donkies_prepare()

        Emulator.emulate_dwolla_transfers()

        a = e.debt_accounts[0]
        a.transfer_share = 100
        a.save()

        a = e.debt_accounts[1]
        a.transfer_share = 0
        a.save()

        TransferUser.objects.process_to_model()
        assert TransferUser.objects.count() == 1
        qs = TransferDonkies.objects.filter(is_processed_to_user=False)
        assert qs.count() == 0

    @pytest.mark.django_db
    def test_process_to_model04(self):
        """
        User doesn't have debt accounts.
        TransferUser model should get 0 items.
        """

        e = Emulator(num_debt_accounts=0)
        e.init()
        e.run_transfer_prepare()
        e.run_transfer_donkies_prepare()

        Emulator.emulate_dwolla_transfers()

        TransferUser.objects.process_to_model()
        assert TransferUser.objects.count() == 0
