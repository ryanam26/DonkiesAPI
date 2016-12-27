import json
import pytest
from .import base
from .factories import UserFactory


class TestCustomer(base.Mixin):
    @pytest.mark.django_db
    def test_create(self, client):
        """
        Test API endpoint for creating customer.
        """
        user = UserFactory(email='bob@gmail.com')
        client = self.get_auth_client(user)

        url = '/v1/customer'
        dic = {
            'type': 'personal',
        }
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 201
