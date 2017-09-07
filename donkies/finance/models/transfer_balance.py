from datetime import datetime
from decimal import *
from django.db import models
from django.contrib import admin
from django.contrib.postgres.fields import JSONField

from finance.models.funding_source import FundingSource
from finance.models.account import Account


class TransferBalanceManaget(models.Manager):

    def create_transfer_balance(self, funding_source, account,
                                transfer, direction):
        transfer = self.model(
            funding_source=funding_source,
            account=account,
            _links=transfer['_links'],
            amount=Decimal(transfer['amount']['value']),
            currency=transfer['amount']['currency'],
            transfer_id=transfer['id'],
            created=datetime.strptime(
                transfer['created'].split('.')[0], "%Y-%m-%dT%H:%M:%S"
            ),
            transfer_direction=direction,
            clearing=transfer['clearing'] if 'clearing' in transfer else None
        )

        transfer.save()

        return transfer


class TransferBalance(models.Model):
    """
    Save all transfer to customers dwolla balance
    """
    PENDING = 'pending'
    PROCESSED = 'processed'

    STATUS = (
        (PENDING, 'pending'),
        (PROCESSED, 'processed')
    )
    ACCOUNT_DWOLLA = 'account --> dwolla_balance'
    DWOLLA_ACCOUNT = 'dwolla_balance --> account'

    TRANSFER_DIRECTION = (
        (ACCOUNT_DWOLLA, 'account --> dwolla_balance'),
        (DWOLLA_ACCOUNT, 'dwolla_balance --> account')
    )

    funding_source = models.ForeignKey(FundingSource,
                                       related_name='funding_sources',
                                       blank=False)
    account = models.ForeignKey(Account, related_name='accounts', blank=False)
    _links = JSONField(blank=False, null=True, default=None)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    currency = models.CharField(max_length=255, blank=False)
    created = models.DateTimeField(auto_now_add=False, blank=False)
    transfer_id = models.CharField(max_length=255, blank=False)
    status = models.CharField(max_length=100, choices=STATUS,
                              default='pending')
    transfer_direction = models.CharField(max_length=255,
                                          choices=TRANSFER_DIRECTION,
                                          default='account --> dwolla_balance')
    clearing = JSONField(blank=False, null=True, default=None)

    objects = TransferBalanceManaget()

    def __str__(self):
        return self.transfer_direction


@admin.register(TransferBalance)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        'account',
        'transfer_direction',
    )
    readonly_fields = (
        'funding_source',
        'amount',
        'currency',
        'created',
        'transfer_id',
        '_links',
        'status',
        'clearing',
    )
