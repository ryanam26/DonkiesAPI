import pytest
import time
from django.conf import settings
from rest_framework.test import APIClient
from web.models import User, Token
from finance.models import Credentials, Member, Account, Transaction
from .import base


@pytest.fixture(scope='session')
def django_db_setup():
    pass


class TestAtrium(base.Mixin):
    """
    Test calls to atrium API.
    Tests on real database (only getting).
    New results do not saved.

    Using any passwords got following:
    1) INITIATED -> AUTHENTICATED -> TRANSFERRED -> COMPLETED
    2) INITIATED -> AUTHENTICATED -> RECEIVED -> COMPLETED
    3) INITIATED -> REQUESTED -> AUTHENTICATED -> TRANSFERRED -> COMPLETED

    COMPLETED status means that all accounts and transactions
              are ready and can be queried from atrium.
    """
    TEST_CODE = 'mxbank'
    TEST_USERNAME = 'test_atrium'
    TEST_PASSWORD = 'can_be_any'

    # Passwords for particular scenario.
    TEST_CHALLENGE = 'challenge'
    TEST_OPTIONS = 'options'
    TEST_IMAGE = 'image'
    TEST_BAD_REQUEST = 'BAD_REQUEST'
    TEST_UNAUTHORIZED = 'UNAUTHORIZED'
    TEST_INVALID = 'INVALID'
    TEST_LOCKED = 'LOCKED'
    TEST_DISABLED = 'DISABLED'
    TEST_SERVER_ERROR = 'SERVER_ERROR'
    TEST_UNAVAILABLE = 'UNAVAILABLE'

    TEST_CORRECT_ANSWER = 'correct'

    def init(self):
        self.email = settings.TEST_USER_EMAIL
        self.password = settings.TEST_USER_PASSWORD

    def get_auth_client(self, user):
        client = APIClient()
        token = Token.objects.get(user_id=user.id)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        return client

    def get_credentials(self):
        """
        Mock MXBank credentials for creating member.
        """
        login = Credentials.objects.get(
            institution__code=self.TEST_CODE, field_name='LOGIN')
        password = Credentials.objects.get(
            institution__code=self.TEST_CODE, field_name='PASSWORD')
        return [
            {'guid': login.guid, 'value': self.TEST_USERNAME},
            {'guid': password.guid, 'value': self.TEST_PASSWORD},
        ]

    @pytest.mark.django_db
    def get_member_data(self):
        """
        Data from creating member.
        """
        self.init()
        user = User.objects.get(email=self.email)
        return {
            'user_guid': user.guid,
            'code': self.TEST_CODE,
            'credentials': self.get_credentials()
        }

    @property
    def real_member(self):
        """
        Real response from atrium when create new member.
        """
        return {
            'guid': 'MBR-c8920871-c461-0a06-8ece-c4bc33e95855',
            'successfully_aggregated_at': None,
            'status': 'INITIATED',
            'institution_code': 'chase',
            'metadata': None,
            'identifier': None,
            'aggregated_at': '2016-11-11T17:12:36+00:00',
            'user_guid': 'USR-bbd4be28-38bd-f870-5c77-6241952bfb36',
            'name': 'Chase Bank'
        }

    @property
    def real_account(self):
        """
        Real account (real response from API.)
        """
        return {
            'payment_due_at': None,
            'total_account_value': None,
            'available_balance': 1000.0,
            'name': 'Test Account 4',
            'apr': None,
            'is_closed': False,
            'available_credit': None,
            'matures_on': None,
            'balance': 1000.0,
            'user_guid': 'USR-168d3809-7656-6dd2-8979-521ac7651d51',
            'subtype': None,
            'updated_at': '2016-11-11T21:31:35+00:00',
            'member_guid': 'MBR-f4641905-a49f-f3df-f508-9f34549eb687',
            'guid': 'ACT-1db63ba8-d9e2-c8a9-23a9-092069528393',
            'started_on': None,
            'credit_limit': None,
            'original_balance': None,
            'apy': None,
            'type': 'CREDIT_CARD',
            'institution_code': 'mxbank',
            'interest_rate': None,
            'day_payment_is_due': None,
            'last_payment_at': None,
            'last_payment': None,
            'minimum_payment': None,
            'minimum_balance': None,
            'created_at': '2016-11-11T21:31:35+00:00',
            'payoff_balance': None
        }

    @property
    def real_transaction(self):
        """
        Real transaction (real response from API)
        """
        return {
            'latitude': None,
            'original_description': 'Pyrefunc Disc Filter',
            'created_at': '2016-11-11T21:31:36+00:00',
            'status': 'POSTED',
            'longitude': None,
            'is_expense': True,
            'account_guid': 'ACT-1db63ba8-d9e2-c8a9-23a9-092069528393',
            'type': 'DEBIT',
            'description': 'Pyrefunc Disc Filter',
            'is_bill_pay': False,
            'is_fee': False,
            'top_level_category': 'Uncategorized',
            'user_guid': 'USR-168d3809-7656-6dd2-8979-521ac7651d51',
            'category': 'Uncategorized',
            'is_income': False,
            'amount': 28.79,
            'guid': 'TRN-f3043632-4459-ac54-20f5-91abac855bc6',
            'transacted_at': '2016-11-11T12:00:00+00:00',
            'is_payroll_advance': False,
            'merchant_category_code': None,
            'is_direct_deposit': False,
            'date': '2016-11-11',
            'updated_at': '2016-11-11T21:31:36+00:00',
            'check_number': None,
            'member_guid': 'MBR-f4641905-a49f-f3df-f508-9f34549eb687',
            'posted_at': '2016-11-11T12:00:00+00:00',
            'memo': None,
            'is_overdraft_fee': False
        }

    @pytest.mark.django_db
    def test_user(self, client):
        """
        When user created in django, by celery it should be
        registered in atrium.
        """
        self.init()
        user = User.objects.get(email=self.email)
        assert user.guid is not None
        assert user.is_atrium_created is True

    @pytest.mark.django_db
    def test_create_account_and_transaction(self, client):
        """
        Test creating using example of real data from API.
        """
        self.init()
        m = Member.objects.get_or_create_member(**self.get_member_data())
        d = self.real_account
        d['member_guid'] = m.guid
        acc = Account.objects.create_account(d)
        assert acc.guid == d['guid']

        d = self.real_transaction
        d['member_guid'] = m.guid
        d['account_guid'] = acc.guid
        tr = Transaction.objects.create_transaction(d)
        assert tr.guid == d['guid']

    @pytest.mark.django_db
    def test_api(self, client):
        """
        Create member for test user and "mxbank" institution.
        After member created, fetch and create accounts and transactions.
        """
        self.init()
        user = User.objects.get(email=self.email)
        m = Member.objects.get_or_create_member(**self.get_member_data())
        guid = m.guid
        print(m.status)
        for _ in range(7):
            status = Member.objects.get_status(m)
            print(status)
            time.sleep(1)

        m = Member.objects.get(id=m.id)
        assert m.guid == guid

        # Get user accounts.
        res = Account.objects.get_atrium_accounts(user.guid)
        l = res['accounts']
        print('Accounts from API: ', len(l))

        # Create accounts in database
        # Substitude member_guid to value that exist for sure.
        for d in l:
            d['member_guid'] = m.guid

        Account.objects.create_accounts(user.guid, l)
        qs = Account.objects.filter(member__user__guid=user.guid)
        print('Accounts created: ', qs.count())

        acc = Account.objects.filter(member__user__guid=user.guid).first()

        # Get user transactions.
        res = Transaction.objects.get_atrium_transactions(user.guid)
        l = res['transactions']
        print('Transactions from API: ', len(l))

        # Substitude account_guid to value that exists for sure.
        for d in l:
            d['account_guid'] = acc.guid

        Transaction.objects.create_transactions(user.guid, l)
        qs = Transaction.objects.filter(
            account__member__user__guid=user.guid)
        print('Transactions created: ', qs.count())
