import pytest
from finance.models import Institution
from .factories import UserFactory, InstitutionFactory, ItemFactory
from .import base


class TestInstitutions(base.Mixin):
    """
    Sandbox institutions.

    First Gingham Credit Union
    First Platypus Bank
    Houndstooth Bank
    Tartan Bank
    Tattersall Federal Credit Union
    """
    def init(self):
        # Besides gettings, creates few institutions
        InstitutionFactory.get_institution()

    @pytest.mark.django_db
    def test_suggest01(self, client):
        """
        Test institutions suggest endpoint.
        """
        self.init()
        user = UserFactory(email='bob@gmail.com')
        client = self.get_auth_client(user)

        url = '/v1/institutions_suggest?value=ta'
        response = client.get(url)
        assert response.status_code == 200

        rd = response.json()
        assert len(rd) > 0

    @pytest.mark.django_db
    def test_suggest02(self, client):
        """
        Test institutions suggest endpoint.
        When user already created item for particular institution,
        this institution should be excluded from suggested result.
        Test institutions: Tartan Bank
        """
        self.init()

        user = UserFactory(email='bob@gmail.com')
        client = self.get_auth_client(user)

        url = '/v1/institutions_suggest?value=tartan'
        response = client.get(url)
        assert response.status_code == 200

        rd = response.json()
        assert len(rd) == 1

        i = Institution.objects.filter(name__icontains='Tartan').first()
        ItemFactory.get_item(user=user, institution=i)

        # As soon as user has Tartan Bank, it should be excluded
        # from suggest results.

        url = '/v1/institutions_suggest?value=tartan'
        response = client.get(url)
        assert response.status_code == 200

        rd = response.json()
        assert len(rd) == 0
