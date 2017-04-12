import pytest

from ach.models import TransferStripe, TransferUser, TransferDebt
from donkies.tests.services.stripe.emulator import Emulator
from donkies.tests import base


class TestApi(base.Mixin):
    """
    Testing transfers API endpoints.
    """
    @pytest.mark.django_db
    def test_get_transfer_prepare(self, client):
        e = Emulator()
        e.init()
        e.run_transfer_prepare()
        client = self.get_auth_client(e.user)

        url = '/v1/transfers_prepare'
        response = client.get(url)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_get_transfer_stripe(self, client):
        e = Emulator()
        e.init()
        e.create_stripe_transfers(90)
        e.run_process_users()

        count = TransferStripe.objects.count()
        assert count > 0
        client = self.get_auth_client(e.user)

        url = '/v1/transfers_stripe'
        response = client.get(url)
        assert response.status_code == 200
        rd = response.json()
        assert len(rd) == count

    @pytest.mark.django_db
    def test_get_transfer_user(self, client):
        e = Emulator()
        e.init()
        e.create_stripe_transfers(90)
        e.run_process_users()
        client = self.get_auth_client(e.user)

        count = TransferUser.objects.count()
        assert count > 0

        url = '/v1/transfers_user'
        response = client.get(url)
        assert response.status_code == 200
        rd = response.json()
        assert len(rd) == count

    @pytest.mark.django_db
    def test_get_transfer_debt(self, client):
        e = Emulator()
        e.init()
        e.create_stripe_transfers(90)
        e.run_process_users()
        client = self.get_auth_client(e.user)

        count = TransferDebt.objects.count()
        assert count > 0

        url = '/v1/transfers_debt'
        response = client.get(url)
        assert response.status_code == 200
        rd = response.json()
        assert len(rd) == count
