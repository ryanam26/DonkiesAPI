import pytest

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
