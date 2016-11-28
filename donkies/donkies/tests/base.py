import pytest
from rest_framework.test import APIClient
from web.models import Token


class Mixin:
    @pytest.mark.django_db
    def setup(self):
        """
        The data available for all fake tests.
        """
        pass

    @pytest.mark.django_db
    def login(self):
        token = Token.objects.get(user__email=self.email)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def get_auth_client(self, user):
        client = APIClient()
        token = Token.objects.get(user_id=user.id)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        return client
