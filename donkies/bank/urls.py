from django.conf.urls import url
from .import views as v

urlpatterns = [
    url(
        r'^(?P<version>(v1))/create_funding_source_by_iav$',
        v.CreateFundingSourceByIAV.as_view(),
        name='create_funding_source_by_iav'),

    url(
        r'^(?P<version>(v1))/customer$',
        v.CustomerDetail.as_view(),
        name='customer'),

    url(
        r'^(?P<version>(v1))/funding_sources$',
        v.FundingSources.as_view(),
        name='funding_sources'),

    url(
        r'^(?P<version>(v1))/get_iav_token/(?P<dwolla_customer_id>[a-z0-9-]+)$',
        v.GetIAVToken.as_view(),
        name='get_iav_token'),

    url(
        r'^(?P<version>(v1))/transfers_debt$',
        v.TransfersDebt.as_view(),
        name='transfers_debt'),

    url(
        r'^(?P<version>(v1))/transfers_donkies$',
        v.TransfersDonkies.as_view(),
        name='transfers_donkies'),

    url(
        r'^(?P<version>(v1))/transfers_user$',
        v.TransfersUser.as_view(),
        name='transfers_user'),
]
