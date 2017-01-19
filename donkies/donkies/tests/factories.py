import decimal
import factory
import random
from django.utils import timezone
from faker import Faker
from web.models import User, Email
from finance.models import Account, Member, Institution, Transaction


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('email',)

    address1 = Faker().address()[:50]
    city = Faker().city()
    date_of_birth = '1980-01-01'
    state = Faker().state_abbr()
    postal_code = Faker().postalcode()
    ssn = Faker().ssn()
    phone = '5613069507'
    is_active = True
    is_confirmed = True


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
    def get_transaction(account=None):
        if not account:
            account = AccountFactory.get_account()

        return TransactionFactory(
            account=account,
            amount=TransactionFactory.generate_amount()
        )
