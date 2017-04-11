from django.conf.urls import url
from .import views as v

urlpatterns = [
    url(
        r'^(?P<version>(v1))/transfers_debt$',
        v.TransfersDebt.as_view(),
        name='transfers_debt'),

    url(
        r'^(?P<version>(v1))/transfers_stripe$',
        v.TransfersStripe.as_view(),
        name='transfers_stripe'),

    url(
        r'^(?P<version>(v1))/transfers_user$',
        v.TransfersUser.as_view(),
        name='transfers_user'),
]
