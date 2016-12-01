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
            'firstName': 'Bob',
            'lastName': 'Smith',
            'email': 'bob@gmail.com',
            'type': 'personal',
            'address1': '99-99 33rd St',
            'address2': '99-99 33rd St',
            'city': 'Some City',
            'state': 'NY',
            'postal_code': '11111',
            'date_of_birth': '1970-01-01',
            'ssn': '111-11-1111',
            'phone': '1111111111'
        }
        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 201
        print(response.content)
