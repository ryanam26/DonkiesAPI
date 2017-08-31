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

        return {
            'funding_soure': founding_instance.funding_sources_url,
            'dwolla_balance': founding_instance.dwolla_balance_id
        }

    raise Exception('Insufficient funds')


def charge_application(amount, user):
    """
    Try to get funding source
    make tranfer via DwollaApi
    """
    from finance.services.dwolla_api import DwollaAPI

    try:
        funding_source = get_funding_source(user, amount)
    except Exception as error:
        raise Exception(error)

    dw = DwollaAPI()
    dw.transfer_to_customer_dwolla_balance(
        funding_source['funding_soure'],
        funding_source['dwolla_balance'],
        amount
    )


def get_total_in_stash(user_id):
    Stat = apps.get_model('finance', 'Stat')
    balance = Stat.objects.get_funds_in_coinstash(user_id)
    return balance


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

    def calculate_roundups(self, roundup=None, *args, **kwargs):
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

        self.save()


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
