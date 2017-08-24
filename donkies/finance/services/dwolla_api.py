from web.serializers import UserSerializer
from django.apps import apps
from django.conf import settings
from rest_framework.response import Response
import dwollav2
from decimal import *


class DwollaAPI:

    def __init__(self):
        env = settings.DWOLLA_ENV
        if env not in ['production', 'development', 'sandbox']:
            raise ValueError('Incorrect value for DWOLLA_ENV in settings.')

        self.client = dwollav2.Client(id=settings.DWOLLA_ID_SANDBOX,
                                      secret=settings.DWOLLA_SECRET_SANDBOX,
                                      environment=env)
        self.app_token = self.client.Auth.client()

    def get_api_url(self):
        """
        For RAW requests.
        """
        if settings.DWOLLA_API_MODE == 'PROD':
            return 'https://api.dwolla.com/'
        return 'https://api-uat.dwolla.com/'

    def validate_user(self, user):
        """
        Check user credentials
        """
        User = apps.get_model('web', 'User')
        user_dict = User.objects.values().get(email=user.email)

        serialiser = UserSerializer(data=user_dict)

        return serialiser.is_valid(raise_exception=True)

    def create_verified_customer(self, user):
        """
        Create customer on Dwolla
        """
        valid_user = self.validate_user(user)

        if not valid_user:
            return Response(valid_user, status=400)

        request_body = {
            'firstName': user.first_name,
            'lastName': user.last_name,
            'email': user.email,
            'type': user.type,
            'address1': user.address1,
            'city': user.city,
            'state': user.state,
            'postalCode': user.postal_code,
            'dateOfBirth': str(user.date_of_birth),
            'ssn': user.ssn
        }

        customer = self.app_token.post('customers', request_body)
        user.dwolla_verified_url = customer.headers['location']
        user.save()

        res = False
        if user.dwolla_verified_url:
            res = True
        return res

    def create_dwolla_funding_source(self, user, processor_token):
        """
        Create funding source on Dwolla
        """
        Customer = apps.get_model('bank', 'Customer')
        customer = Customer.objects.get(user=user)
        customer_url = '{}customers/{}'.format(
            self.get_api_url(), customer.dwolla_id)

        request_body = {'plaidToken': processor_token,
                        'name': '{} {}'.format(
                            user.first_name,
                            user.last_name
                        )}
        try:
            customer = self.app_token.post(
                '{}/fudinng-sources'.format(customer_url), request_body)
        except Exception as e:
            raise e

        return customer.headers['location']

    def save_funding_source(self, item, user, funding_source):
        FundingSource = apps.get_model('finance', 'FundingSource')

        return FundingSource.objects.create(
            user=user,
            funding_sources_url=funding_source,
            item=item
        )
