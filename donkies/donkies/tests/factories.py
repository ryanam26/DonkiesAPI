import factory
# from oauth2_provider.models import Application
from django.utils import timezone
from faker import Faker
from web.models import User, Email
from finance.models import Account, Member, Institution


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


class AccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Account

    member = factory.SubFactory(MemberFactory)
    guid = factory.Sequence(lambda n: 'guid{0}'.format(n))
    uid = factory.Sequence(lambda n: 'uid{0}'.format(n))
    name = factory.Sequence(lambda n: 'name{0}'.format(n))
    balance = 1000
    created_at = timezone.now()
    type = Account.LOAN
    updated_at = timezone.now()
