import datetime
import json
import pytest
from faker import Faker
from web.models import User
from .factories import UserFactory
from .import base


class TestUser(base.Mixin):
    @pytest.mark.django_db
    def test_get(self, client):
        """
        Test user get.
        """
        user = UserFactory(email='bob@gmail.com')
        client = self.get_auth_client(user)

        url = '/v1/user'
        response = client.get(url)
        assert response.status_code == 200

        rd = response.json()
        assert user.email == rd['email']

    @pytest.mark.django_db
    def test_edit(self, client):
        """
        Test user get.
        """
        user = UserFactory(email='bob@gmail.com')
        client = self.get_auth_client(user)

        url = '/v1/user'
        dic = {
            'first_name': 'John',
            'last_name': 'Johnson',
            'address1': 'new address1',
            'address2': 'new address2',
            'city': Faker().city(),
            'state': 'AL',
            'postal_code': Faker().postalcode(),
            'date_of_birth': '1979-09-09',
            'ssn': Faker().ssn()

        }

        data = json.dumps(dic)
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 200

        user = User.objects.get(email=user.email)
        for key, value in dic.items():
            db_value = getattr(user, key)
            if isinstance(db_value, datetime.date):
                assert value == db_value.strftime('%Y-%m-%d')
            else:
                assert value == db_value
