import pytest
from django.conf import settings
from finance.models import Institution
from finance.services.atrium_api import AtriumApi
from .factories import UserFactory
from .import base


@pytest.fixture(scope='module')
def institutions():
    a = AtriumApi()
    d = a.search_institutions(name='Wells Fargo')
    return {'list': d['institutions']}


class TestInstitutions(base.Mixin):
    """
    Test institutions and credentials on Atrium
    PRODUCTION credentials.
    Only fetching data from Atrium.
    """
    WELLS_FARGO_CODE = 'wells_fargo'

    def setup(self):
        """
        Data available for all tests.
        """
        settings.ATRIUM_API_MODE = 'PROD'

    def init(self, institutions):
        for d in institutions:
            Institution.objects.update(**d)

    @pytest.mark.django_db
    def test_update(self, client, institutions):
        """
        Test manager's method "update".
        """
        assert Institution.objects.count() == 0
        self.init(institutions['list'])

        assert Institution.objects.count() > 0

        qs = Institution.objects.filter(code=self.WELLS_FARGO_CODE)
        assert qs.exists() is True

    @pytest.mark.django_db
    def test_suggest(self, client, institutions):
        """
        Test institutions suggest endpoint.
        """
        self.init(institutions['list'])
        user = UserFactory(email='bob@gmail.com')
        client = self.get_auth_client(user)

        url = '/v1/institutions_suggest?value=we'
        response = client.get(url)
        assert response.status_code == 200

        rd = response.json()
        assert len(rd) > 0

    @pytest.mark.django_db
    def test_get_credentials(self, client):
        """
        Get credentials from Atrium for particular institution.
        """
        a = AtriumApi()
        res = a.get_credentials(self.WELLS_FARGO_CODE)
        assert len(res) > 0

    @pytest.mark.django_db
    def test_get_credentials_by_id(self, client, institutions):
        """
        Test API endpoint.
        """
        self.init(institutions['list'])
        user = UserFactory(email='bob@gmail.com')
        client = self.get_auth_client(user)

        i = Institution.objects.get(code=self.WELLS_FARGO_CODE)

        url = '/v1/credentials/live/id/{}'.format(i.id)
        response = client.get(url)
        assert response.status_code == 200

        l = response.json()
        assert len(l) > 0

    @pytest.mark.django_db
    def test_get_credentials_by_code(self, client, institutions):
        """
        Test API endpoint.
        """
        self.init(institutions['list'])
        user = UserFactory(email='bob@gmail.com')
        client = self.get_auth_client(user)

        i = Institution.objects.get(code=self.WELLS_FARGO_CODE)

        url = '/v1/credentials/live/code/{}'.format(i.code)
        response = client.get(url)
        assert response.status_code == 200

        l = response.json()
        assert len(l) > 0
