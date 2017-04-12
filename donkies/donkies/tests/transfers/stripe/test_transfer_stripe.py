import pytest
from freezegun import freeze_time
from django.utils import timezone
from django.db.models import Sum
from donkies.tests.services.stripe.emulator import Emulator
from finance.models import TransferPrepare
from ach.models import TransferStripe
from donkies.tests import base


class TestTransferStripe(base.Mixin):
    @pytest.mark.django_db
    def test_01(self):
        """
        Create Stripe transfer.
        After prepare transfer from TransferPrepare,
        TransferStripe should get 1 row for 1 user.
        The account is user's funding source.
        Transfers to Stripe are created on the last day of the month.

        1) TransferStripe should have 1 row
        2) The second transfer for the same user in the same day
           should not work.
        3) The amount (total roundup) in TransferStripe row
           should be equal to total sum in TransferPrepare rows.
        4) All TransferPrepare should be processed:
           (is_processed=True)
        """
        e = Emulator()
        e.init()
        Emulator.run_transfer_prepare()
        qs = TransferPrepare.objects.all()
        assert qs.count() > 1

        sum = TransferPrepare.objects.filter(
            is_processed=False, account__item__user=e.user)\
            .aggregate(Sum('roundup'))['roundup__sum']

        # Required for real request to Stripe API in
        # TransferStripe.objects.process_transfers()
        account = e.user.get_funding_source_account()
        access_token, account_id = self.get_access_token()
        account.plaid_id = account_id
        account.save()

        item = account.item
        item.access_token = access_token
        item.save()

        dt = self.get_last_date_of_the_month()
        with freeze_time(dt.strftime('%Y-%m-%d %H:%M:%S')):
            # Emulate last day of the month
            TransferStripe.objects.process_transfers()

            assert TransferStripe.objects.can_process_user(e.user.id) is True

            # 1
            assert TransferStripe.objects.count() == 1

            tr = TransferStripe.objects.first()
            # "created_at" is not match to our mock date
            # Make this condition.
            tr.created_at = timezone.now()
            tr.save()

            # 2
            assert TransferStripe.objects.can_process_user(e.user.id) is False

        # 3
        qs = TransferStripe.objects.filter(account__item__user=e.user)
        assert qs.first().amount == sum

        # 4
        qs = TransferPrepare.objects.filter(is_processed=False)
        assert qs.count() == 0

    @pytest.mark.django_db
    def test_02(self):
        """
        Update Stripe transfer.
        """
        e = Emulator()
        e.init()
        Emulator.run_transfer_prepare()
        qs = TransferPrepare.objects.all()
        assert qs.count() > 1

        # Required for real request to Stripe API in
        # TransferStripe.objects.process_transfers()
        account = e.user.get_funding_source_account()
        access_token, account_id = self.get_access_token()
        account.plaid_id = account_id
        account.save()

        item = account.item
        item.access_token = access_token
        item.save()

        dt = self.get_last_date_of_the_month()
        with freeze_time(dt.strftime('%Y-%m-%d %H:%M:%S')):
            # Emulate last day of the month
            TransferStripe.objects.process_transfers()
            assert TransferStripe.objects.count() == 1

        # In sandbox all transfers automatically become SUCCEEDED
        # after creation. (On production few days).
        TransferStripe.objects.update_transfers()
        ts = TransferStripe.objects.first()
        assert ts.status == TransferStripe.SUCCEEDED
        assert ts.paid is True
