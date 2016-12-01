from django.conf.urls import url
from .import views as v

urlpatterns = [
    url(
        r'^(?P<version>(v1))/customer$',
        v.CustomerDetail.as_view(),
        name='customer'),
]
