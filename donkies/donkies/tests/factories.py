import factory
import uuid
# from oauth2_provider.models import Application
from django.utils import timezone
from web.models import User, Email
from finance.models import Account, Member, Institution


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('email',)

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
    guid = uuid.uuid4().hex
    identifier = factory.Sequence(lambda n: 'identifier{0}'.format(n))
    name = factory.Sequence(lambda n: 'name{0}'.format(n))
    status = Member.SUCCESS


class AccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Account

    member = factory.SubFactory(MemberFactory)
    guid = uuid.uuid4().hex
    uid = uuid.uuid4().hex
    name = factory.Sequence(lambda n: 'name{0}'.format(n))
    balance = 1000
    created_at = timezone.now()
    type = Account.CHECKING
    updated_at = timezone.now()


# class ApplicationFactory(factory.django.DjangoModelFactory):
#     class Meta:
#         model = Application
#         django_get_or_create = ('user',)

#     name = 'Web app'
#     client_type = Application.CLIENT_CONFIDENTIAL
#     authorization_grant_type = Application.GRANT_PASSWORD
