import pytest
import time
from bank.services.dwolla_api import DwollaApi
from finance.models import TransferDonkies
from bank.models import Customer
from .. import base
from ..emulator import Emulator
from ..factories import CustomerFactory


@pytest.mark.django_db
class TestTransferDonkiesDwolla(base.Mixin):
    """
    Tests that use Dwolla API.
    Run from US server.
    """
    def setup(self):
        """
        Setup customer and funding source for all tests.
        Run on every test.
        Can not use setup_class here, because need database access
        for creating customer.

        Get or create verified customer.
        Get or create customer's verified funding source account.
        """
        # self = cls()
        self.dw = DwollaApi()

        c = self.get_dwolla_customer()
        if c is None:
            c = self.create_customer()
            if not c:
                raise ValueError('Can not create customer')
        self.customer = c

        fs = self.get_funding_source()
        if fs is None:
            fs = self.dw.create_test_funding_source(self.customer['id'])
            if fs is None:
                raise ValueError('Can not create funding source')

        self.funding_source = fs
        # print(self.customer)
        # print(self.funding_source)

        for c in self.dw.get_customers():
            if c['status'] == 'verified':
                for fs in self.dw.get_funding_sources(c['id']):
                    if fs['status'] == 'verified':
                        print(self.dw.get_funding_source_balance(fs['id']))
                        print('------------')



    def create_customer(self):
        customer = CustomerFactory.get_customer()
        Customer.objects.create_dwolla_customer(customer.id)
        customer.refresh_from_db()
        return self.dw.get_customer(customer.dwolla_id)

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
    def notest01(self):
        """
        Do not run each time, because too many customers
        will be created in Dwolla.
        """
        customer = CustomerFactory.get_customer()
        Customer.objects.create_dwolla_customer(customer.id)
        customer.refresh_from_db()
        assert customer.dwolla_id is not None

    @pytest.mark.django_db
    def notest02(self):
        """
        Do not run each time, because too many customers
        will be created in Dwolla.
        """
        customer = CustomerFactory.get_customer()
        Customer.objects.create_dwolla_customer(customer.id)
        customer.refresh_from_db()
        assert customer.dwolla_id is not None

        Customer.objects.initiate_dwolla_customer(customer.id)
        customer.refresh_from_db()
        assert customer.dwolla_type is not None
        assert customer.created_at is not None
        assert customer.status is not None

    @pytest.mark.django_db
    def notest03(self):
        customer = CustomerFactory.get_customer()
        data = Customer.objects.get_customer_data_for_create_request(customer)
        c1 = self.dw.create_customer(data)
        c2 = self.dw.create_customer(data)
        assert c1 == c2

    @pytest.mark.django_db
    def test04(self):
        return
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
        tds.save()

        TransferDonkies.objects.initiate_dwolla_transfer(tds.id)
        tds.refresh_from_db()

        assert tds.is_initiated is True
        assert tds.initiated_at is not None
        assert tds.updated_at is not None
        assert tds.dwolla_id is not None

    @pytest.mark.django_db
    def notestxx(self):
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
        tds.amount = 1
        tds.save()

        TransferDonkies.objects.initiate_dwolla_transfer(tds.id)

        for _ in range(5):
            TransferDonkies.objects.update_dwolla_transfer(tds.id)
            tds.refresh_from_db()
            print(tds.status)

            if tds.status and tds.status != TransferDonkies.PENDING:
                break
            time.sleep(2)

        assert tds.status == TransferDonkies.PROCESSED
        assert tds.is_sent is True
        assert tds.sent_at is not None
        assert tds.updated_at is not None
