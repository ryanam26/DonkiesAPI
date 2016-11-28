import pytest
from .import base
from finance.models import Account, LinkDebt
from .factories import (
    AccountFactory, InstitutionFactory, MemberFactory, UserFactory)


class TestLinking(base.Mixin):
    @pytest.mark.django_db
    def test_share(self, client):
        user = UserFactory(email='bob@gmail.com')
        i = InstitutionFactory(code='code1')
        m1 = MemberFactory(user=user, institution=i)
        a1 = AccountFactory(member=m1, type=Account.LOAN)

        i = InstitutionFactory(code='code2')
        m2 = MemberFactory(user=user, institution=i)
        a2 = AccountFactory(member=m2, type=Account.LOAN)

        i = InstitutionFactory(code='code3')
        m3 = MemberFactory(user=user, institution=i)
        a3 = AccountFactory(member=m3, type=Account.LOAN)

        # Create first link
        # Share should be equal 100%,
        # doesn't matter what share pass to function.
        ld1 = LinkDebt.objects.create_link(user, a1, 55)
        assert ld1.share == 100

        # Create second link with share 30%
        # Should get: link1 = 70%, link2 = 30%
        ld2 = LinkDebt.objects.create_link(user, a2, 30)
        ld1.refresh_from_db()
        ld2.refresh_from_db()
        assert ld1.share == 70
        assert ld2.share == 30

        # Create third link with share 40%
        # Should get: link1 = 50%, link2 = 10%, link3 = 40%
        ld3 = LinkDebt.objects.create_link(user, a3, 40)
        ld1.refresh_from_db()
        ld2.refresh_from_db()
        ld3.refresh_from_db()
        assert ld1.share == 50
        assert ld2.share == 10
        assert ld3.share == 40
