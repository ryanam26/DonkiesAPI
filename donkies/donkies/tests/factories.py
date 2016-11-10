import factory
# from oauth2_provider.models import Application
from web.models import User, Email


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


# class ApplicationFactory(factory.django.DjangoModelFactory):
#     class Meta:
#         model = Application
#         django_get_or_create = ('user',)

#     name = 'Web app'
#     client_type = Application.CLIENT_CONFIDENTIAL
#     authorization_grant_type = Application.GRANT_PASSWORD
