from django.conf.urls import url
from donkiesoauth2.views import register_user


urlpatterns = [
    url(r'^developers/sign_up/$', register_user, name="dev_sign_up"),
]
