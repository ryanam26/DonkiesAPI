import pytest
from .import base
from .factories import (
    AccountFactory, InstitutionFactory, MemberFactory, UserFactory)


class TestLinking(base.Mixin):
    @pytest.mark.django_db
    def test_share(self, client):
        user = UserFactory(email='bob@gmail.com')
        i = InstitutionFactory(code='mxbank')
        m = MemberFactory(user=user, institution=i)
        a = AccountFactory(member=m)
        print(a)
