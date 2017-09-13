from django.conf.urls import url
from .import views as v

urlpatterns = [
    url(
        r'^(?P<version>[v1]+)/accounts$',
        v.Accounts.as_view(),
        name='accounts'),

    url(
        r'^(?P<version>[v1]+)/accounts/delete/(?P<pk>\d+)$',
        v.AccountDetail.as_view(),
        name='account'),

    url(
        r'^(?P<version>[v1]+)/accounts/(?P<pk>\d+)$',
        v.AccountDetailRetrive.as_view(),
        name="retrive_account"),

    url(
        r'^(?P<version>[v1]+)/accounts/edit_share$',
        v.AccountsEditShare.as_view(),
        name='accounts_edit_share'),

    url(
        r'^(?P<version>[v1]+)/accounts/set_active/(?P<pk>\d+)$',
        v.AccountsSetActive.as_view(),
        name='accounts_set_active'),

    url(
        r'^(?P<version>[v1]+)/accounts/set_account_number/(?P<pk>\d+)$',
        v.AccountsSetNumber.as_view(),
        name='accounts_set_number'),

    url(
        r'^(?P<version>[v1]+)/accounts/set_funding_source/(?P<pk>\d+)$',
        v.AccountsSetFundingSource.as_view(),
        name='accounts_set_funding_source'),

    url(
        r'^(?P<version>[v1]+)/accounts/set_primary/(?P<pk>\d+)$',
        v.AccountsSetPrimary.as_view(),
        name='accounts_set_primary'),

    url(r'^(?P<version>[v1]+)/accounts/pause$',
        v.PauseAccont.as_view(),
        name='PauseAccont'),

    url(
        r'^(?P<version>[v1]+)/institutions_suggest$',
        v.InstitutionsSuggest.as_view(),
        name='institutions_suggest'),

    url(
        r'^(?P<version>[v1]+)/debt_institutions$',
        v.DebtInstitutions.as_view(),
        name='debt_institutions'),

    # url(
    #     r'^(?P<version>[v1]+)/institutions$',
    #     v.Institutions.as_view(),
    #     name='institutions'),
    url(
        r'^(?P<version>[v1]+)/tranfer_balance$',
        v.BalanceTransaction.as_view(),
        name='tranfer_balance'),
    url(
        r'^(?P<version>[v1]+)/institutions/(?P<pk>\d+)$',
        v.InstitutionDetail.as_view(),
        name='institution'),

    url(
        r'^(?P<version>[v1]+)/items$',
        v.Items.as_view(),
        name='items'),

    url(
        r'^(?P<version>[v1]+)/items/fake_roundup$',
        v.FakeRoundups.as_view(),
        name='fake_roundups'),

    url(
        r'^(?P<version>[v1]+)/items/transfer_to_checking_account$',
        v.TransferChecking.as_view(),
        name='tansfer_checking'),

    url(r'^(?P<version>[v1]+)/items/create_transaction$',
        v.CreateTransaction.as_view(),
        name='create_transaction'),

    url(r'^(?P<sersion>[v1]+)/make_transfer$',
        v.MakeTransfer.as_view(),
        name='make_transfer'),

    url(r'^(?P<version>[v1]+)/transfer/set_the_minimum_value_for_transfers$',
        v.SetMinimumValueForTransfer.as_view(),
        name='set_min_val'),

    url(
        r'^(?P<version>[v1]+)/items/(?P<guid>\w+)$',
        v.ItemDetail.as_view(),
        name='item_detail'),

    url(
        r'^(?P<version>[v1]+)/lenders$',
        v.Lenders.as_view(),
        name='lenders'),

    url(
        r'^(?P<version>[v1]+)/lenders/(?P<id>\d+)$',
        v.LenderDetail.as_view(),
        name='lender_detail'),

    url(
        r'^(?P<version>[v1]+)/plaid/webhooks$',
        v.PlaidWebhooks.as_view(),
        name='plaid_webhooks'),

    url(
        r'^(?P<version>[v1]+)/stat$',
        v.StatView.as_view(),
        name='stat'),

    url(
        r'^(?P<version>[v1]+)/transactions$',
        v.Transactions.as_view(),
        name='transactions'),

    url(
        r'^(?P<version>[v1]+)/transfers_prepare$',
        v.TransfersPrepare.as_view(),
        name='transfers_prepare'),
]
