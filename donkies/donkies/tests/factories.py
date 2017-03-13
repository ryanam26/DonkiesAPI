import datetime
import decimal
import factory
import random
import uuid
from django.utils import timezone
from faker import Faker
from web.models import User, Email
from finance.models import (
    Account, Member, Institution, Transaction, TransferDonkies)
from bank.models import Customer


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('email',)

    first_name = Faker().first_name()
    last_name = Faker().last_name()
    address1 = Faker().street_address()
    city = Faker().city()
    date_of_birth = '1980-01-01'
    state = Faker().state_abbr()
    postal_code = Faker().postalcode()
    ssn = Faker().ssn()
    is_active = True
    is_confirmed = True
    confirmed_at = timezone.now() - datetime.timedelta(days=200)


class EmailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Email
        django_get_or_create = ('code',)


class InstitutionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Institution
        django_get_or_create = ('code',)

    name = factory.Sequence(lambda n: 'Name{0}'.format(n))
    url = factory.Sequence(lambda n: 'Url{0}'.format(n))


class MemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Member

    user = factory.SubFactory(UserFactory)
    institution = factory.SubFactory(InstitutionFactory)
    guid = factory.Sequence(lambda n: 'guid{0}'.format(n))
    identifier = factory.Sequence(lambda n: 'identifier{0}'.format(n))
    name = factory.Sequence(lambda n: 'name{0}'.format(n))
    status = Member.SUCCESS

    @staticmethod
    def get_member(user=None, name=None):
        if not user:
            user = UserFactory(email=Faker().email())
        code = Faker().word() + str(random.randint(1000, 9999))
        institution = InstitutionFactory(code=code)
        if not name:
            name = Faker().word()
        return MemberFactory(
            user=user, institution=institution, name=name)


class AccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Account

    member = factory.SubFactory(MemberFactory)
    guid = factory.Sequence(lambda n: 'guid{0}'.format(n))
    uid = factory.Sequence(lambda n: 'uid{0}'.format(n))
    name = factory.Sequence(lambda n: 'name{0}'.format(n))
    balance = 1000
    created_at = timezone.now()
    type = Account.CHECKING
    updated_at = timezone.now()

    @staticmethod
    def get_account(member=None, type=Account.CHECKING):
        if not member:
            member = MemberFactory.get_member()
        return AccountFactory(member=member, type=type)


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    account = factory.SubFactory(AccountFactory)
    guid = factory.Sequence(lambda n: 'guid{0}'.format(n))
    uid = factory.Sequence(lambda n: 'uid{0}'.format(n))
    amount = decimal.Decimal('10.56')

    @staticmethod
    def generate_amount():
        dollars = random.randint(3, 30)
        cents = random.randint(0, 99)
        return decimal.Decimal('{}.{}'.format(dollars, cents))

    @staticmethod
    def get_transaction(account=None, created_at=None):
        if not account:
            account = AccountFactory.get_account()

        if not created_at:
            created_at = timezone.now()

        return TransactionFactory(
            account=account,
            amount=TransactionFactory.generate_amount(),
            created_at=created_at,
            updated_at=created_at,
            transacted_at=created_at,
            posted_at=created_at
        )


class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer

    user = factory.SubFactory(UserFactory)

    @staticmethod
    def get_customer(email=None):
        if email is None:
            email = Faker().email()

        user = UserFactory(email=email)
        return Customer.objects.create_customer(user)


class TransferDonkiesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TransferDonkies

    account = factory.SubFactory(AccountFactory)

    @staticmethod
    def get_transfer(account=None, sent_at=None):
        if not account:
            account = AccountFactory.get_account()

        if not sent_at:
            sent_at = timezone.now()

        return TransferDonkiesFactory(
            account=account,
            amount=TransactionFactory.generate_amount(),
            created_at=sent_at,
            initiated_at=sent_at,
            sent_at=sent_at,
            updated_at=sent_at,
            is_initiated=True,
            is_sent=True,
            status=TransferDonkies.PROCESSED,
            dwolla_id=uuid.uuid4().hex
        )
