import json
import pytest
import time
from web.models import User
from finance.models import Credentials, Challenge, Member, Account, Transaction
from finance import tasks
from .import base
from .factories import InstitutionFactory, UserFactory


class TestAtrium(base.Mixin):
    """
    Test calls to atrium API.
    Each test clean previous atrium data and creates new.
    Run only on sandbox credentials.
    Celery should be stopped when running tests.
    All test call manually required tasks.

    Using any passwords got following:
    1) INITIATED -> AUTHENTICATED -> TRANSFERRED -> COMPLETED
    2) INITIATED -> AUTHENTICATED -> RECEIVED -> COMPLETED
    3) INITIATED -> REQUESTED -> AUTHENTICATED -> TRANSFERRED -> COMPLETED

    COMPLETED status means that all accounts and transactions
              are ready and can be queried from atrium.
    """
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
        """
        Run on each test.
        """
        print('--- Clean Atrium data.')
        User.objects.clean_atrium()

        self.user = UserFactory(email='bob@gmail.com')
        self.create_mx_bank()
        self.create_mx_bank_credentials()

        # Create user in Atrium
        print('--- Create user in Atrium.')
        User.objects.create_atrium_user(self.user.id)
        self.user.refresh_from_db()

    def create_mx_bank(self):
        InstitutionFactory(
            code='mxbank', name='MX Bank', url='https://www.mx.com')

    def create_mx_bank_credentials(self):
        i = InstitutionFactory(code='mxbank')
        cred = Credentials(
            institution=i,
            guid='CRD-9f61fb4c-912c-bd1e-b175-ccc7f0275cc1',
            field_name='LOGIN',
            label='Username',
            type='LOGIN'
        )
        cred.save()

        cred = Credentials(
            institution=i,
            guid='CRD-e3d7ea81-aac7-05e9-fbdd-4b493c6e474d',
            field_name='PASSWORD',
            label='Password',
            type='PASSWORD'
        )
        cred.save()

    def get_credentials(self, passwd):
        login = Credentials.objects.get(
            institution__code='mxbank', field_name='LOGIN')
        password = Credentials.objects.get(
            institution__code='mxbank', field_name='PASSWORD')
        return [
            {'guid': login.guid, 'value': self.TEST_USERNAME},
            {'guid': password.guid, 'value': passwd},
        ]

    def get_credentials_for_api(self, passwd):
        """
        Credentials for API.
        """
        login = Credentials.objects.get(
            institution__code='mxbank', field_name='LOGIN')
        password = Credentials.objects.get(
            institution__code='mxbank', field_name='PASSWORD')
        return [
            {'field_name': login.field_name, 'value': self.TEST_USERNAME},
            {'field_name': password.field_name, 'value': passwd},
        ]

    @pytest.mark.django_db
    def test_create_member01(self):
        """
        Test API endpoint - create member.
        Call to Atrium API in Member manager.
        """
        self.init()
        client = self.get_auth_client(self.user)

        url = '/v1/members'
        dic = {
            'institution_code': 'mxbank',
            'credentials': self.get_credentials_for_api(self.TEST_PASSWORD)
        }
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        # print(response.content)
        assert response.status_code == 201

    @pytest.mark.django_db
    def test_create_member02(self):
        """
        Create member with correct credentials.
        Should get status COMPLETED.
        """
        self.init()
        print('--- Test success:')
        m = Member.objects.get_or_create_member(
            self.user.guid, 'mxbank', self.get_credentials(self.TEST_PASSWORD))

        success_result = False
        for _ in range(7):
            am = Member.objects.get_atrium_member(m)
            print(am.status)
            if am.status == 'COMPLETED':
                success_result = True
                break
            time.sleep(1)

        if not success_result:
            assert False

    @pytest.mark.django_db
    def test_create_member03(self):
        """
        Create member with incorrect credentials.
        Should get status DENIED.
        """
        self.init()
        print('--- Test invalid:')
        m = Member.objects.get_or_create_member(
            self.user.guid, 'mxbank', self.get_credentials(self.TEST_INVALID))

        success_result = False
        for _ in range(7):
            am = Member.objects.get_atrium_member(m)
            print(am.status)
            if am.status == 'DENIED':
                success_result = True
                break
            time.sleep(1)

        if not success_result:
            assert False

    @pytest.mark.django_db
    def test_create_member04(self):
        """
        Test CHALLENGED status.
        Create member with credentials to get CHALLENGE.
        1) Should get status CHALLENGED.
        2) Run celery task that should create challenges in database.
        3) Test API endoint, that resumes member.
        Should get status COMPLETED.
        """
        self.init()
        print('--- Test challenge:')
        m = Member.objects.get_or_create_member(
            self.user.guid,
            'mxbank',
            self.get_credentials(self.TEST_CHALLENGE))

        success_result = False
        for _ in range(7):
            am = Member.objects.get_atrium_member(m)
            print(am.status)
            if am.status == 'CHALLENGED':
                success_result = True
                break
            time.sleep(1)

        if not success_result:
            assert False

        # Call task manually, after that database should have challenges
        tasks.get_member(m.id)
        qs = Challenge.objects.filter(member=m.id)
        assert qs.count() > 0

        challenges = []
        for ch in qs:
            d = {'label': ch.label, 'value': self.TEST_CORRECT_ANSWER}
            challenges.append(d)

        # Call API to resume member.
        url = '/v1/members/resume/{}'.format(m.identifier)
        dic = {'challenges': challenges}
        data = json.dumps(dic)
        client = self.get_auth_client(self.user)
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 204

        # Should get COMPLETED status
        success_result = False
        for _ in range(7):
            am = Member.objects.get_atrium_member(m)
            print(am.status)
            if am.status == 'COMPLETED':
                success_result = True
                break
            time.sleep(1)

        if not success_result:
            assert False

    @pytest.mark.django_db
    def test_accounts_transactions(self):
        """
        Test fetching accounts and transactions from Atrium.
        1) Create member
        2) Update user (calling celery task)
        After that accounts and transactions should be in database.
        """
        self.init()
        print('--- Test accounts and transactions:')
        m = Member.objects.get_or_create_member(
            self.user.guid, 'mxbank', self.get_credentials(self.TEST_PASSWORD))

        assert Account.objects.filter(member=m).count() == 0
        assert Transaction.objects.filter(account__member=m).count() == 0

        success_result = False
        for _ in range(7):
            am = Member.objects.get_atrium_member(m)
            print(am.status)
            if am.status == 'COMPLETED':
                success_result = True
                break
            time.sleep(1)

        if not success_result:
            assert False

        tasks.update_user(self.user.id)

        assert Account.objects.filter(member=m).count() > 0
        assert Transaction.objects.filter(account__member=m).count() > 0
