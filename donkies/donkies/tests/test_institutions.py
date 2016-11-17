import pytest
from .import base
from finance.models import Institution, Credentials


class TestInstitutions(base.Mixin):
    """
    Tests fetching and updating institutions
    and their credentials.
    nd can be queried from atrium.
    """
    @pytest.mark.django_db
    def test_01(self, client):
        # Test update institution
        assert Institution.objects.count() == 0
        Institution.objects.update_list()
        assert Institution.objects.count() > 0

        # Test update credentials
        Institution.objects.all().update(is_update=True)
        assert Credentials.objects.all().count() == 0
        Institution.objects.update_credentials()
        assert Credentials.objects.all().count() > 0
