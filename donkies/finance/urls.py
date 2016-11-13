from django.conf.urls import url
from .import views as v

urlpatterns = [
    url(
        r'^(?P<version>(v1))/accounts$',
        v.Accounts.as_view(),
        name='accounts'),

    url(
        r'^(?P<version>(v1))/credentials/(?P<institution_code>\w+)$',
        v.CredentialsList.as_view(),
        name='credentials'),

    url(
        r'^(?P<version>(v1))/members$',
        v.Members.as_view(),
        name='members'),

    url(
        r'^(?P<version>(v1))/members/(?P<identifier>\w+)$',
        v.MemberDetail.as_view(),
        name='member'),

    url(
        r'^(?P<version>(v1))/transactions$',
        v.Transactions.as_view(),
        name='transactions'),
]
