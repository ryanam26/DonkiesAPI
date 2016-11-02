from django.conf.urls import url
from donkiesoauth2.views import api_auth_success

urlpatterns = [
    url(r'^api/v1/logged_in/.*', api_auth_success),
]