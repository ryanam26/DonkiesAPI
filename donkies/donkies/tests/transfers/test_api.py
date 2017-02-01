import pytest

from donkies.tests.services.emulator import Emulator
from ..import base


class TestApi(base.Mixin):
    """
    Testing transfers API endpoints.
    """
    def setup(self):
        e = Emulator()
        e.init()
        e.run_transfer_prepare()
        e.run_transfer_donkies_prepare()
        Emulator.emulate_dwolla_transfers()
        self.user = e.user

    @pytest.mark.django_db
    def test_get_transfer_prepare(self, client):
        client = self.get_auth_client(self.user)

        url = '/v1/transfers_prepare'
        response = client.get(url)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_get_transfer_donkies(self, client):
        e = Emulator()
        e.init()
        e.run_transfer_prepare()
        e.run_transfer_donkies_prepare()
        Emulator.emulate_dwolla_transfers()
        client = self.get_auth_client(e.user)

        url = '/v1/transfers_donkies'
        response = client.get(url)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_get_transfer_user(self, client):
        e = Emulator()
        e.init()
        e.run_transfer_prepare()
        e.run_transfer_donkies_prepare()

        Emulator.emulate_dwolla_transfers()
        Emulator.emulate_transfers_to_user()
        client = self.get_auth_client(e.user)

        url = '/v1/transfers_user'
        response = client.get(url)
        assert response.status_code == 200
