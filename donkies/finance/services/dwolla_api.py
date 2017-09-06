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

    def get_balance_funding_source(self, balance_id):
        return '{}funding-sources/{}'.format(
            self.get_api_url(), balance_id
        )

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

        if user.is_parent:
            child = user.childs.all().first()
            customer = Customer.objects.get(user=child)
        else:
            customer = Customer.objects.get(user=user)

        customer_url = '{}customers/{}'.format(
            self.get_api_url(), customer.dwolla_id)
        request_body = {'plaidToken': processor_token,
                        'name': '{} {} {} checking'.format(
                            user.first_name,
                            user.last_name,
                            'Parent' if user.is_parent else ''
                        )}
        try:
            customer = self.app_token.post(
                '%s/funding-sources' % customer_url, request_body)
        except Exception as e:
            raise e

        return customer.headers['location']

    def save_funding_source(self, item, user,
                            funding_source, dwolla_balance_id):

        FundingSource = apps.get_model('finance', 'FundingSource')

        return FundingSource.objects.create(
            user=user,
            funding_sources_url=funding_source,
            item=item,
            dwolla_balance_id=dwolla_balance_id
        )

    def transfer_to_customer_dwolla_balance(self, funding_source,
                                            balance_id, amount):
        request_body = {
            '_links': {
                'source': {
                    'href': funding_source
                },
                'destination': {
                    'href': self.get_balance_funding_source(balance_id)
                }
            },
            'amount': {
                'currency': 'USD',
                'value': str(round(Decimal(amount), 2))
            }
        }

        transfer = self.app_token.post('transfers', request_body)
        return transfer.headers['Location']

    def transfer_from_balance_to_check_acc(self, funding_source,
                                           balance_id):

        balance_fundong_source = self.get_balance_funding_source(balance_id)

        try:
            balance = self.app_token.get(
                '%s/balance' % balance_fundong_source
            )
        except Exception as e:
            raise e

        if Decimal(balance.body['balance']['value']) > 0:

            request_body = {
                '_links': {
                    'source': {
                        'href': balance_fundong_source
                    },
                    'destination': {
                        'href': funding_source
                    }
                },
                'amount': {
                    'currency': balance.body['balance']['currency'],
                    'value': balance.body['balance']['value']
                }
            }

            try:
                transfer = self.app_token.post('transfers', request_body)
            except Exception as e:
                raise e

            return {
                'message': self.app_token.get(
                    transfer.headers['Location']).body,
                'status': 201
            }

        return {
            'message': 'Dwolla balance is empty',
            'status': 400
        }
