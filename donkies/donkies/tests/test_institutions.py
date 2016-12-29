import pytest
from .import base
from finance.models import Institution, Credentials
from .factories import InstitutionFactory, UserFactory


class TestInstitutions(base.Mixin):
    """
    Tests fetching and updating institutions
    and their credentials.
    nd can be queried from atrium.
    """
    @pytest.mark.django_db
    def notest_01(self, client):
        # Test update institution
        assert Institution.objects.count() == 0
        Institution.objects.update_list()
        assert Institution.objects.count() > 0

        # Test update credentials
        Institution.objects.all().update(is_update=True)
        assert Credentials.objects.all().count() == 0
        Institution.objects.update_credentials()
        assert Credentials.objects.all().count() > 0

    @pytest.mark.django_db
    def test_suggest(self, client):
        """
        Test institutions suggest endpoint.
        """
        InstitutionFactory(code='code1', name='name1')
        InstitutionFactory(code='code2', name='name2')
        InstitutionFactory(code='code3', name='name3')

        user = UserFactory(email='bob@gmail.com')
        client = self.get_auth_client(user)

        url = '/v1/institutions_suggest?value=na'
        response = client.get(url)
        assert response.status_code == 200

        rd = response.json()
        assert len(rd) == 3
