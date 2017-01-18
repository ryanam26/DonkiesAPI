import pytest
from .. import base
from ..factories import UserFactory


class TestTransaction(base.Mixin):
    @pytest.mark.django_db
    def test(self):
        user = UserFactory(email='bob@gmail.com')
        print(user)
