from django.conf.urls import url
from .import views as v

urlpatterns = [
    url(
        r'^(?P<version>(v1))/accounts$',
        v.Accounts.as_view(),
        name='accounts'),

    url(
        r'^(?P<version>(v1))/accounts/(?P<pk>\d+)$',
        v.AccountDetail.as_view(),
        name='account'),

    url(
        r'^(?P<version>(v1))/accounts/edit_share$',
        v.AccountsEditShare.as_view(),
        name='accounts_edit_share'),

    url(
        r'^(?P<version>(v1))/accounts/set_active/(?P<pk>\d+)$',
        v.AccountsSetActive.as_view(),
        name='accounts_set_active'),

    url(
        r'^(?P<version>(v1))/accounts/set_funding_source/(?P<pk>\d+)$',
        v.AccountsSetFundingSource.as_view(),
        name='accounts_set_funding_source'),

    url(
        r'^(?P<version>(v1))/credentials/code/(?P<institution_code>\w+)$',
        v.CredentialsListByCode.as_view(),
        name='credentials_by_code'),

    url(
        r'^(?P<version>(v1))/credentials/id/(?P<institution_id>\w+)$',
        v.CredentialsListById.as_view(),
        name='credentials_by_id'),

    url(
        r'^(?P<version>(v1))/credentials/live/code/(?P<institution_code>\w+)$',
        v.CredentialsLiveListByCode.as_view(),
        name='credentials_live_by_code'),

    url(
        r'^(?P<version>(v1))/credentials/live/id/(?P<institution_id>\w+)$',
        v.CredentialsLiveListById.as_view(),
        name='credentials_live_by_id'),

    url(
        r'^(?P<version>(v1))/institutions_suggest$',
        v.InstitutionsSuggest.as_view(),
        name='institutions_suggest'),

    url(
        r'^(?P<version>(v1))/institutions$',
        v.Institutions.as_view(),
        name='institutions'),

    url(
        r'^(?P<version>(v1))/institutions/(?P<pk>\d+)$',
        v.InstitutionDetail.as_view(),
        name='institution'),

    url(
        r'^(?P<version>(v1))/link_debts$',
        v.LinkDebts.as_view(),
        name='link_debts'),

    url(
        r'^(?P<version>(v1))/members$',
        v.Members.as_view(),
        name='members'),

    url(
        r'^(?P<version>(v1))/members/(?P<identifier>\w+)$',
        v.MemberDetail.as_view(),
        name='member'),

    url(
        r'^(?P<version>(v1))/members/resume/(?P<identifier>\w+)$',
        v.MemberResume.as_view(),
        name='member_resume'),

    url(
        r'^(?P<version>(v1))/stat$',
        v.StatView.as_view(),
        name='stat'),

    url(
        r'^(?P<version>(v1))/transactions$',
        v.Transactions.as_view(),
        name='transactions'),

    url(
        r'^(?P<version>(v1))/transfers_donkies$',
        v.TransfersDonkies.as_view(),
        name='transfers_donkies'),

    url(
        r'^(?P<version>(v1))/transfers_prepare$',
        v.TransfersPrepare.as_view(),
        name='transfers_prepare'),

    url(
        r'^(?P<version>(v1))/transfers_user$',
        v.TransfersUser.as_view(),
        name='transfers_user'),
]
