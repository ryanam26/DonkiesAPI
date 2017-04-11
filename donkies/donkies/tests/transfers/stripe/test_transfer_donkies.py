import pytest
from django.db.models import Sum
from donkies.tests.services.emulator import Emulator
from finance.models import TransferPrepare
from bank.models import TransferDonkies, TransferDonkiesFailed
from donkies.tests import base


class TestTransferDonkies(base.Mixin):
    @pytest.mark.django_db
    def test_01(self):
        """
        After prepare transfer from TransferPrepare to
        TransferDonkies, TransferDonkies should get 1 row
        for 1 user. The account is user's funding source.
        """
        # User 1
        e1 = Emulator()
        e1.init()

        # User 2
        e2 = Emulator()
        e2.init()

        Emulator.run_transfer_prepare()
        Emulator.run_transfer_donkies_prepare()

        assert TransferDonkies.objects.count() == 2

    @pytest.mark.django_db
    def test_02(self):
        """
        The amount (total roundup) in TransferDonkies row
        should be equal to total sum in TransferPrepare rows.

        Test for 2 users.
        """
        e1 = Emulator()
        e1.init()

        e2 = Emulator()
        e2.init()

        Emulator.run_transfer_prepare()

        sum1 = TransferPrepare.objects.filter(
            is_processed=False, account__item__user=e1.user)\
            .aggregate(Sum('roundup'))['roundup__sum']

        sum2 = TransferPrepare.objects.filter(
            is_processed=False, account__item__user=e2.user)\
            .aggregate(Sum('roundup'))['roundup__sum']

        Emulator.run_transfer_donkies_prepare()

        assert TransferDonkies.objects.count() == 2

        qs = TransferDonkies.objects.filter(account__item__user=e1.user)
        assert qs.first().amount == sum1

        qs = TransferDonkies.objects.filter(account__item__user=e2.user)
        assert qs.first().amount == sum2

    @pytest.mark.django_db
    def test_03(self):
        """
        After processing transfers from TransferPrepare to
        TransferFonkies, Transfer prepare shouldn't have
        is_processed=False, everything should be processed.
        """
        e = Emulator()
        e.init()
        e.make_transfer_prepare_condition()

        Emulator.run_transfer_prepare()
        qs = TransferPrepare.objects.filter(is_processed=False)
        assert qs.count() > 0

        Emulator.run_transfer_donkies_prepare()

        qs = TransferPrepare.objects.filter(is_processed=False)
        assert qs.count() == 0

    @pytest.mark.django_db
    def test_04(self):
        """
        Test moving TransferDonkies item to TransferDonkiesFailed.
        TransferDonkiesFailed should have the copy of the item.
        Original item should be deleted from TransferDonkies.
        """
        e = Emulator(num_debit_accounts=1)
        e.init()
        e.make_transfer_prepare_condition()

        Emulator.run_transfer_prepare()
        Emulator.run_transfer_donkies_prepare()

        tds = TransferDonkies.objects.first()
        tds.failure_code = 'R99'
        tds.is_failed = True
        tds.save()

        TransferDonkies.objects.move_failed(tds.id)

        tdf = TransferDonkiesFailed.objects.first()

        assert tds.dwolla_id == tdf.dwolla_id
        assert tds.amount == tdf.amount
        assert tds.status == tdf.status
        assert tds.created_at == tdf.created_at
        assert tds.initiated_at == tdf.initiated_at
        assert tds.updated_at == tdf.updated_at
        assert tds.failure_code == tdf.failure_code
        assert tds.is_initiated == tdf.is_initiated
        assert tds.is_failed == tdf.is_failed
        assert tds.account == tdf.account

        assert TransferDonkies.objects.filter(id=tds.id).exists() is False
