import pytest
import time
from django.conf import settings
from bank.services.dwolla_api import DwollaApi
from finance.models import TransferDonkies
from bank.models import Customer
from donkies.tests.services.emulator import Emulator
from ..factories import CustomerFactory
from .. import base


TEST_EMAIL = 'test@example.com'


def get_or_create_customer():
    """
    Get or create dwolla customer.
    """
    dw = DwollaApi()
    customer = dw.get_customer_by_email(TEST_EMAIL)
    if customer is not None:
        return customer
    customer = CustomerFactory.get_customer(email=TEST_EMAIL)
    Customer.objects.create_dwolla_customer(customer.id)
    customer.refresh_from_db()
    return dw.get_customer(customer.dwolla_id)


def get_or_create_funding_source(customer, name='My Bank'):
    """
    Returns funding source (bank) or creates verified
    funding source (bank) in Dwolla for test customer.

    name is used to simulate different test cases.

    name = "R01" Insufficient Funds:
             failing from the source bank account.

    name = "R01-late" Simulate funds failing from the
            source bank account post-settlement.
            Must click "Process bank transfers" twice.
    """
    dw = DwollaApi()
    for fs in dw.get_funding_sources(customer['id']):
        if fs['status'] == 'verified' and fs['type'] == 'bank':
            # Set funding source's name.
            dw.edit_funding_source_name(fs['id'], name)
            return fs

    data = {
        'routingNumber': '222222226',
        'accountNumber': '123456789',
        'type': 'savings',
        'name': name
    }
    print('Creating funding source --------')
    id = dw.create_funding_source(customer['id'], data)
    fs = dw.get_funding_source(id)
    print(fs)

    print('Initiating micro-deposits -------')
    res = dw.initiate_micro_deposits(fs['id'])
    print(res)

    print('Get status of micro-deposits -------')
    res = dw.get_micro_deposits(fs['id'])

    print('Verifying funding source -------')
    res = dw.verify_micro_deposits(
        fs['id'], '0.05', '0.05')
    print(res)

    print('Checking the status of funding source -------')
    fs = dw.get_funding_source(id)
    print(fs['status'])
    return fs


@pytest.fixture(scope='module')
def dwolla():
    """
    Fixture for all tests.
    Customer and funding source from Dwolla
    for test customer.
    """
    customer = get_or_create_customer()
    fs = get_or_create_funding_source(customer)
    data = {
        'customer': customer,
        'funding_source': fs
    }
    return data


class TestTransferDonkiesDwolla(base.Mixin):
    """
    Tests that use Dwolla API.
    Run from US server.
    """
    def setup(self):
        self.dw = DwollaApi()

    @pytest.mark.django_db
    def notest01(self, dwolla):
        """
        Do not run each time, because too many customers
        will be created in Dwolla.

        Test create customer.
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

        Test create and initiate customer.
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
        """
        Do not run each time, because too many customers
        will be created in Dwolla.

        Test create customer, then create the same customer again.
        Instead of error, should get the same customer.
        """
        customer = CustomerFactory.get_customer()
        data = Customer.objects.get_customer_data_for_create_request(customer)
        c1 = self.dw.create_customer(data)
        c2 = self.dw.create_customer(data)
        assert c1 == c2

    @pytest.mark.django_db
    def test04(self, dwolla):
        """
        Test initiate transfer.
        """
        funding_source = dwolla['funding_source']

        e = Emulator(num_debit_accounts=1)
        e.init()

        sum = e.user.get_not_processed_roundup_sum()
        settings.TRANSFER_TO_DONKIES_MIN_AMOUNT = sum - 1

        Emulator.run_transfer_prepare()
        Emulator.run_transfer_donkies_prepare()

        # Exchange dwolla_id for mock debit account with
        # real funding source dwolla_id
        account = e.debit_accounts[0]
        fs = account.funding_source
        fs.dwolla_id = funding_source['id']
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
    def test05(self, dwolla):
        """
        Test initiate and update transfer with success status.
        """
        funding_source = dwolla['funding_source']

        e = Emulator(num_debit_accounts=1)
        e.init()

        sum = e.user.get_not_processed_roundup_sum()
        settings.TRANSFER_TO_DONKIES_MIN_AMOUNT = sum - 1

        Emulator.run_transfer_prepare()
        Emulator.run_transfer_donkies_prepare()

        # Exchange dwolla_id for mock debit account with
        # real funding source dwolla_id from API
        account = e.debit_accounts[0]
        fs = account.funding_source
        fs.dwolla_id = funding_source['id']
        fs.save()

        tds = TransferDonkies.objects.first()
        tds.save()

        TransferDonkies.objects.initiate_dwolla_transfer(tds.id)

        for _ in range(20):
            TransferDonkies.objects.update_dwolla_transfer(
                tds.id, is_test=True)
            tds.refresh_from_db()

            print('Transfer status: ', tds.status)

            # Process sandbox transfers
            self.dw.press_sandbox_button()

            if tds.status and tds.status != TransferDonkies.PENDING:
                break
            time.sleep(5)

        assert tds.status == TransferDonkies.PROCESSED
        assert tds.is_sent is True
        assert tds.sent_at is not None
        assert tds.updated_at is not None

    @pytest.mark.django_db
    def test06(self, dwolla):
        """
        Should be last test as it changes fixture's funding_source to R01.

        Test initiate and update transfer with insufficient funds.
        1) Should get failed status.
        2) Update failure_code.
        3) Failure code should be "R01"
        """
        customer = dwolla['customer']
        funding_source = get_or_create_funding_source(customer, name='R01')

        e = Emulator(num_debit_accounts=1)
        e.init()

        sum = e.user.get_not_processed_roundup_sum()
        settings.TRANSFER_TO_DONKIES_MIN_AMOUNT = sum - 1

        Emulator.run_transfer_prepare()
        Emulator.run_transfer_donkies_prepare()

        # Exchange dwolla_id for mock debit account with
        # real funding source dwolla_id from API
        account = e.debit_accounts[0]
        fs = account.funding_source
        fs.dwolla_id = funding_source['id']
        fs.save()

        tds = TransferDonkies.objects.first()
        tds.save()

        TransferDonkies.objects.initiate_dwolla_transfer(tds.id)

        for _ in range(20):
            TransferDonkies.objects.update_dwolla_transfer(
                tds.id, is_test=True)
            tds.refresh_from_db()

            print('Transfer status: ', tds.status)

            # Process sandbox transfers
            self.dw.press_sandbox_button()

            if tds.status and tds.status != TransferDonkies.PENDING:
                break
            time.sleep(5)

        assert tds.status == TransferDonkies.FAILED
        assert tds.is_failed is True
        assert tds.failure_code is None

        TransferDonkies.objects.update_dwolla_failure_code(tds.id)
        tds.refresh_from_db()
        assert tds.failure_code == 'R01'
