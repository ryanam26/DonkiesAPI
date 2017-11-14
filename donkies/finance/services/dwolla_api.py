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

    def get_transfer_url(self, transfer_id):
        return '{}transfers/{}'.format(self.get_api_url(), transfer_id)

    def get_balance_funding_source(self, balance_id):
        return '{}funding-sources/{}'.format(
            self.get_api_url(), balance_id
        )

    def validate_user(self, user):
        """
        Check user credentials
        """
        from web.serializers import UserSerializer

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
                        'name': '{} {} {} {}'.format(
                            user.first_name,
                            user.last_name,
                            'savings' if user.is_parent else 'checking',
                            '(parent)' if user.is_parent else '',
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

    def transfer_from_balance_to_check_acc(self, user):
        FundingSource = apps.get_model('finance', 'FundingSource')
        Account = apps.get_model('finance', 'Account')

        accounts = Account.objects.filter(
            item__user=user,
            is_funding_source_for_transfer=True,
            subtype='checking'
        )
        if len(accounts) is 0:
            return {
                'message': 'Funding source does not exist.',
                'status': 400
            }
        account = accounts.first()

        funding_source = FundingSource.objects.filter(
            item=account.item).first()

        funding_source_url = funding_source.funding_sources_url
        balance_id = funding_source.dwolla_balance_id

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
                        'href': funding_source_url
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

            fees = self.app_token.get(transfer.headers['Location'])

            TransferBalance = apps.get_model('finance', 'TransferBalance')
            TransferBalance.objects.create_transfer_balance(
                funding_source, account,
                fees.body, 'dwolla_balance --> account'
            )

            return {
                'message': fees.body
            }

        return {
            'message': 'Dwolla balance is empty'
        }

    def suspend_customer(self, user):
        Customer = apps.get_model('bank', 'Customer')
        customer_url = self.get_api_url() + "customers/" \
            + Customer.objects.filter(user=user).first().dwolla_id
        request_body = {
            "status": "deactivated"
        }
        customer = self.app_token.post(customer_url, request_body)

        return customer.body['status']
