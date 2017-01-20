import pytest
from .. import base
from ..emulator import Emulator
from bank.services.dwolla_api import DwollaApi
from finance.models import TransferDonkies


class TestTransferDonkiesDwolla(base.Mixin):
    """
    Tests that use Dwolla API.
    Run from US server.
    """
    @pytest.mark.django_db
    def setup(self):
        """
        Setup customer and funding source for all tests.
        Get or create verified customer.
        Get or create customer's verified funding source account.
        """
        self.dw = DwollaApi()
        c = self.get_dwolla_customer()
        if c is None:
            c = self.dw.create_test_customer()
            if not c:
                raise ValueError('Can not create customer')
        self.customer = c

        fs = self.get_funding_source()
        if fs is None:
            fs = self.dw.create_test_funding_source(self.customer['id'])
            if fs is None:
                raise ValueError('Can not create funding source')

        self.funding_source = fs

    def get_dwolla_customer(self):
        for c in self.dw.get_customers():
            if c['status'] == 'verified':
                return c
        return None

    def get_funding_source(self):
        for fs in self.dw.get_funding_sources(self.customer['id']):
            if fs['status'] == 'verified':
                return fs
        return None

    @pytest.mark.django_db
    def test01(self):
        e = Emulator(num_debit_accounts=1)
        e.init()
        e.run_transfer_prepare()
        e.run_transfer_donkies_process_prepare()

        # Exchange dwolla_id for mock debit account with
        # real funding source dwolla_id from API
        account = e.debit_accounts[0]
        fs = account.funding_source
        fs.dwolla_id = self.funding_source['id']
        fs.save()

        tds = TransferDonkies.objects.first()
        TransferDonkies.objects.initiate_dwolla_transfer(tds.id)

        tds.refresh_from_db()

        assert tds.is_initiated is True
        assert tds.initiated_at is not None
        assert tds.updated_at is not None
        assert tds.dwolla_id is not None

    @pytest.mark.django_db
    def test02(self):
        e = Emulator(num_debit_accounts=1)
        e.init()
        e.run_transfer_prepare()
        e.run_transfer_donkies_process_prepare()

        # Exchange dwolla_id for mock debit account with
        # real funding source dwolla_id from API
        account = e.debit_accounts[0]
        fs = account.funding_source
        fs.dwolla_id = self.funding_source['id']
        fs.save()

        tds = TransferDonkies.objects.first()
        TransferDonkies.objects.initiate_dwolla_transfer(tds.id)
