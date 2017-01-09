import pytest
from rest_framework.test import APIClient
from web.models import User


class Mixin:
    @pytest.mark.django_db
    def setup(self):
        """
        The data available for all fake tests.
        """
        pass

    @pytest.mark.django_db
    def login(self):
        user = User.objects.get(user__email=self.email)
        token = user.get_token()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def get_auth_client(self, user):
        client = APIClient()
        user = User.objects.get(id=user.id)
        token = user.get_token()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        return client
