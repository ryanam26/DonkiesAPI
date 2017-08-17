from django.db import transaction
from django.contrib import admin
from django.db import models
from django.apps import apps
from django.conf import settings
from decimal import *
import dwollav2
import logging

from web.models import User

logger = logging.getLogger('app')


def get_funding_source(user, amount):
    """
    Check user balance before return
    funding source
    """
    FundingSource = apps.get_model('finance', 'FundingSource')
    Account = apps.get_model('finance', 'Account')

    account = Account.objects.filter(item__user=user, is_primary=True).first()

    if account.balance > amount:
        founding_instance = FundingSource.objects.get(item=account.item)

        return founding_instance.funding_sources_url

    raise Exception('Insufficient funds')


def charge_application(amount, user):
    """
    Try to get funding source
    make tranfer via DwollaApi
    """
    try:
        funding_source = get_funding_source(user, amount)
    except Exception as error:
        raise Exception(error)

    client = dwollav2.Client(id=settings.DWOLLA_ID_SANDBOX,
                             secret=settings.DWOLLA_SECRET_SANDBOX,
                             environment=settings.DWOLLA_ENV)
    app_token = client.Auth.client()

    root = app_token.get('/')
    account_url = root.body['_links']['account']['href']
    customer_url = user.dwolla_verified_url

    request_body = {
        '_links': {
            'source': {
                'href': funding_source
            },
            'destination': {
                'href': account_url
            }
        },
        'amount': {
            'currency': 'USD',
            'value': str(round(Decimal(amount), 2))
        },
        'metadata': {
            'donkie': 'user reached minimum value',
        }
    }

    transfer = app_token.post('transfers', request_body)

    app_funding_sources = app_token.get('%s/funding-sources' % account_url)
    app_funding_sources = app_funding_sources.body['_embedded']['funding-sources'][1]['_links']['self']['href']


    transfer_request = {
      '_links': {
        'source': {
          'href': app_funding_sources
        },
        'destination': {
          'href': customer_url
        }
      },
      'amount': {
        'currency': 'USD',
        'value': str(round(Decimal(amount), 2))
      },
    }

    transfer = app_token.post('transfers', transfer_request)

    return transfer.headers['location']


def get_total_in_stash(user_id):
    Stat = apps.get_model('finance', 'Stat')
    balance = Stat.objects.get_funds_in_coinstash(user_id)
    return balance['value']


class TransferCalculation(models.Model):
    user = models.ForeignKey(User, related_name='user_calulations')
    roundup_sum = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=0)
    total_roundaps = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=0)
    min_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=5)
    total_in_stash_account = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=0)
    applied_funds = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=0)

    def __str__(self):
        return str(self.user)

    def save(self, roundup=None, *args, **kwargs):
        if roundup is not None:
            self.roundup_sum += round(Decimal(roundup), 2)
            self.total_roundaps += round(Decimal(roundup), 2)

            if self.roundup_sum >= self.min_amount:
                try:
                    temp_diff = self.roundup_sum % self.min_amount
                    amount = self.roundup_sum - temp_diff
                    charge_application(amount, self.user)
                    self.roundup_sum = temp_diff
                    self.total_in_stash_account = Decimal(
                        get_total_in_stash(self.user.id))
                except Exception as error:
                    logger.info(error)

        super().save(*args, **kwargs)


@admin.register(TransferCalculation)
class TransactionAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'roundup_sum',
        'total_roundaps',
        'min_amount',
        'total_in_stash_account',
        'applied_funds',
    )
    readonly_fields = (
        'roundup_sum',
        'total_roundaps',
    )
