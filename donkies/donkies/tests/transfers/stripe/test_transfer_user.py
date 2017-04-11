import datetime
import pytest
from freezegun import freeze_time
from django.db.models import Sum
from django.utils import timezone
from donkies.tests.services.emulator import Emulator
from bank.models import TransferUser, TransferDebt, TransferDonkies
from .. import base


class TestTransferUser(base.Mixin):
    def get_first_day_of_current_month(self):
        return timezone.now().replace(
            hour=0, minute=0, second=0, microsecond=0, day=1)

    def get_first_day_of_previous_month(self):
        dt = self.get_first_day_of_current_month()
        dt = dt - datetime.timedelta(days=1)
        return dt.replace(
            hour=0, minute=0, second=0, microsecond=0, day=1)

    @pytest.mark.django_db
    def test_process01(self):
        """
        User doesn't have debt accounts.
        Should not process.
        """
        e = Emulator(num_debt_accounts=0)
        e.init()
        e.create_dwolla_transfers(60)

        TransferUser.objects.process()
        assert TransferUser.objects.count() == 0

    @pytest.mark.django_db
    def test_process02(self):
        """
        User is_auto_transfer set to False.
        Should not process.
        """
        e = Emulator()
        e.init()
        e.create_dwolla_transfers(60)

        e.user.is_auto_transfer = False
        e.user.save()

        TransferUser.objects.process()
        assert TransferUser.objects.count() == 0

    @pytest.mark.django_db
    def test_process03(self):
        """
        User's minimum amount for transfer is more than
        collected amount.
        Should not process.
        """
        e = Emulator()
        e.init()
        e.create_dwolla_transfers(60)

        e.user.minimum_transfer_amount = 1000000
        e.user.save()

        TransferUser.objects.process()
        assert TransferUser.objects.count() == 0

    @pytest.mark.django_db
    def test_process04(self):
        """
        Should process.
        """
        e = Emulator()
        e.init()
        e.create_dwolla_transfers(60)

        TransferUser.objects.process()
        assert TransferUser.objects.count() > 0

    @pytest.mark.django_db
    def test_process05(self):
        """
        Test running "process" manager's method before 15th of the month.
        It should process all TransferDonkies, from month before previous.
        """
        e = Emulator()
        e.init()
        e.create_dwolla_transfers(60)

        dt = timezone.now().replace(day=14)
        dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        with freeze_time(dt_str):
            dt = self.get_first_day_of_previous_month()

            TransferUser.objects.process()
            qs1 = TransferDonkies.objects.filter(is_processed_to_user=True)
            qs2 = TransferDonkies.objects.filter(sent_at__lt=dt)
            assert qs1.count() == qs2.count()
            assert TransferUser.objects.count() == 1

    @pytest.mark.django_db
    def test_process06(self):
        """
        Test running "process" manager's method after 15th of the month.
        It should process all TransferDonkies, from previous month.
        """
        e = Emulator()
        e.init()
        e.create_dwolla_transfers(30)

        dt = timezone.now().replace(day=15)
        dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        with freeze_time(dt_str):
            dt = self.get_first_day_of_current_month()

            TransferUser.objects.process()
            qs1 = TransferDonkies.objects.filter(is_processed_to_user=True)
            qs2 = TransferDonkies.objects.filter(sent_at__lt=dt)
            assert qs1.count() == qs2.count()
            assert TransferUser.objects.count() == 1

    @pytest.mark.django_db
    def test_process07(self):
        """
        Test 3 debt accounts with share: 33%, 33% and 34%
        """
        e = Emulator(num_debt_accounts=3)
        e.init()
        e.create_dwolla_transfers(60)

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
        TransferUser.objects.process()

        tu = TransferUser.objects.first()
        qs = TransferDebt.objects.filter(tu=tu)
        assert qs.count() == 3

        sum = qs.aggregate(Sum('amount'))['amount__sum']
        assert tu.amount == sum

    @pytest.mark.django_db
    def test_process08(self):
        """
        Test 2 debt accounts with share 99% and 1%
        """
        e = Emulator(num_debt_accounts=2)
        e.init()
        e.create_dwolla_transfers(60)

        a = e.debt_accounts[0]
        a.transfer_share = 99
        a.save()

        a = e.debt_accounts[1]
        a.transfer_share = 1
        a.save()

        TransferUser.objects.process()

        tu = TransferUser.objects.first()
        qs = TransferDebt.objects.filter(tu=tu)
        assert qs.count() == 2

        sum = qs.aggregate(Sum('amount'))['amount__sum']
        assert tu.amount == sum

    @pytest.mark.django_db
    def test_process09(self):
        """
        Test 2 debts accounts with share: 100% and 0%
        TransferUser model should get only 1 item instead of 2.
        """

        e = Emulator()
        e.init()
        e.create_dwolla_transfers(60)

        a = e.debt_accounts[0]
        a.transfer_share = 100
        a.save()

        a = e.debt_accounts[1]
        a.transfer_share = 0
        a.save()

        TransferUser.objects.process()

        tu = TransferUser.objects.first()
        qs = TransferDebt.objects.filter(tu=tu)
        assert qs.count() == 1

        sum = qs.aggregate(Sum('amount'))['amount__sum']
        assert tu.amount == sum

    @pytest.mark.django_db
    def test_process10(self):
        """
        All TransferDonkies that have been processed should be marked
        as is_processed_to_user.
        """
        e = Emulator(num_debt_accounts=1)
        e.init()
        e.create_dwolla_transfers(60)

        TransferUser.objects.process()

        tu = TransferUser.objects.first()
        assert tu.items.filter(is_processed_to_user=False).count() == 0
        assert tu.items.filter(is_processed_to_user=True).count() > 0
