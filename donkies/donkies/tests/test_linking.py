import pytest
from .import base
from finance.models import Account, LinkDebt
from .factories import (
    AccountFactory, InstitutionFactory, MemberFactory, UserFactory)
from finance.services.transfer import TransferService


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

        i = InstitutionFactory(code='code4')
        m4 = MemberFactory(user=user, institution=i)
        a4 = AccountFactory(member=m4, type=Account.LOAN)

        # Create 1st link
        # Share should be equal 100%,
        # doesn't matter what share pass to function.
        ld1 = LinkDebt.objects.create_link(user, a1, 55)
        assert ld1.share == 100

        # Create 2nd link with share 30%
        # Should get: link1 = 70%, link2 = 30%
        ld2 = LinkDebt.objects.create_link(user, a2, 30)
        ld1.refresh_from_db()
        ld2.refresh_from_db()
        assert ld1.share == 70
        assert ld2.share == 30

        # Create 3rd link with share 40%
        # Should get: link1 = 50%, link2 = 10%, link3 = 40%
        ld3 = LinkDebt.objects.create_link(user, a3, 40)
        ld1.refresh_from_db()
        ld2.refresh_from_db()
        ld3.refresh_from_db()
        assert ld1.share == 50
        assert ld2.share == 10
        assert ld3.share == 40

        # Create 4th link with share 60%
        # Should get: link1 = 25%, link2 = 0%, link3 = 15%, link4=60%
        ld4 = LinkDebt.objects.create_link(user, a4, 60)
        ld1.refresh_from_db()
        ld2.refresh_from_db()
        ld3.refresh_from_db()
        ld4.refresh_from_db()
        assert ld1.share == 25
        assert ld2.share == 0
        assert ld3.share == 15
        assert ld4.share == 60

    @pytest.mark.django_db
    def test_transafer(self, client):
        t = TransferService(
            TransferService.mock_transactions(),
            TransferService.mock_accounts())
        t.run()
