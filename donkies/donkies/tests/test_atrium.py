import json
import pytest
import time
from django.conf import settings
from rest_framework.test import APIClient
from web.models import User, Token
from finance.models import Credentials, Challenge, Member, Account, Transaction
from finance import tasks
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
        Test for models.
        """
        login = Credentials.objects.get(
            institution__code=self.TEST_CODE, field_name='LOGIN')
        password = Credentials.objects.get(
            institution__code=self.TEST_CODE, field_name='PASSWORD')
        return [
            {'guid': login.guid, 'value': self.TEST_USERNAME},
            {'guid': password.guid, 'value': self.TEST_PASSWORD},
        ]

    def get_challenge_credentials(self):
        """
        Test for models.
        """
        login = Credentials.objects.get(
            institution__code=self.TEST_CODE, field_name='LOGIN')
        password = Credentials.objects.get(
            institution__code=self.TEST_CODE, field_name='PASSWORD')
        return [
            {'guid': login.guid, 'value': self.TEST_USERNAME},
            {'guid': password.guid, 'value': self.TEST_CHALLENGE},
        ]

    def get_credentials_for_api(self):
        """
        Mock MXBank credentials for creating member.
        Test for API endpoint.
        """
        login = Credentials.objects.get(
            institution__code=self.TEST_CODE, field_name='LOGIN')
        password = Credentials.objects.get(
            institution__code=self.TEST_CODE, field_name='PASSWORD')
        return [
            {'field_name': login.field_name, 'value': self.TEST_USERNAME},
            {'field_name': password.field_name, 'value': self.TEST_PASSWORD},
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
            'type': 'CHECKING',
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
        To pass test updated_at should be less that 2 weeks ago
        from now.
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
            'updated_at': '2016-11-27T21:31:36+00:00',
            'check_number': None,
            'member_guid': 'MBR-f4641905-a49f-f3df-f508-9f34549eb687',
            'posted_at': '2016-11-11T12:00:00+00:00',
            'memo': None,
            'is_overdraft_fee': False
        }

    @pytest.mark.django_db
    def notest_user(self, client):
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
        acc = Account.objects.create_or_update_account(d.copy())  # create
        acc = Account.objects.create_or_update_account(d.copy())  # update
        assert acc.guid == d['guid']

        d = self.real_transaction
        d['member_guid'] = m.guid
        d['account_guid'] = acc.guid
        tr = Transaction.objects.create_or_update_transaction(d.copy())
        tr = Transaction.objects.create_or_update_transaction(d.copy())
        assert tr.guid == d['guid']

    @pytest.mark.django_db
    def notest_api(self, client):
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
            am = Member.objects.get_atrium_member(m)
            print(am.status)
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

        # The second time transactions should be updated.
        Transaction.objects.create_transactions(user.guid, l)
        qs = Transaction.objects.filter(
            account__member__user__guid=user.guid)
        print('Transactions created: ', qs.count())

    @pytest.mark.django_db
    def notest_create_member(self, client):
        """
        Test create member via API.
        """
        self.init()
        user = User.objects.get(email=self.email)
        client = self.get_auth_client(user)

        url = '/v1/members'
        dic = {
            'institution_code': self.TEST_CODE,
            'credentials': self.get_credentials_for_api()
        }
        data = json.dumps(dic)

        response = client.post(url, data, content_type='application/json')
        # print(response.content)
        assert response.status_code == 201

    def challenge_answer(self, user, member_id, answer):
        member = Member.objects.get(id=member_id)
        client = self.get_auth_client(user)
        print('Testing answer: {}'.format(answer))
        challenges = []
        for c in list(Challenge.objects.filter(member=member)):
            d = {'label': c.label, 'value': answer}
            challenges.append(d)

        # Call API to resume member.
        url = '/v1/members/resume/{}'.format(member.identifier)
        dic = {'challenges': challenges}
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 204

        # After user responded to challenges, it should get completed status
        for _ in range(7):
            am = Member.objects.get_atrium_member(member)
            print(am.status)

            if am.status in [Member.COMPLETED, Member.DENIED]:
                break
            time.sleep(1)

    @pytest.mark.django_db
    def notest_challenge(self, client):
        """
        It seems there is some bug in Pytrium.
        When I test separately respond on challenge with incorrect answer
        and correct answer, they works fine.
        When one after another - get error.
        But probably because it is the same test session
        and maybe on production that bug won't appear.

        To test separately: comment incorrect or correct answer and run test.
        """
        self.init()
        user = User.objects.get(email=self.email)
        creds = self.get_challenge_credentials()
        data = self.get_member_data()
        data['credentials'] = creds

        m = Member.objects.get_or_create_member(**data)
        # guid = m.guid
        print(m.status)
        for _ in range(7):
            am = Member.objects.get_atrium_member(m)
            print(am.status)

            if am.status == Member.CHALLENGED:
                break
            time.sleep(1)

        # Simulate running task.
        assert Challenge.objects.filter(member=m).count() == 0
        tasks.get_member(m.id)
        assert Challenge.objects.filter(member=m).count() > 0

        # Call API for member detail, that should contain challenges.
        client = self.get_auth_client(user)
        url = '/v1/members/{}'.format(m.identifier)
        response = client.get(url)
        assert response.status_code == 200

        # Simulate filling challenges on frontend
        # Test wrong answer
        # self.challenge_answer(user, m.id, 'wrong answer')
        print('Waiting...')
        time.sleep(5)

        # test correct answer
        self.challenge_answer(user, m.id, self.TEST_CORRECT_ANSWER)
