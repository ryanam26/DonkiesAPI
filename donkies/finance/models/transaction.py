import datetime
import logging
import math
import uuid
from django.db import models
from django.contrib import admin
from django.apps import apps
from django.db import transaction
from django.contrib.postgres.fields import JSONField
from web.models import ActiveModel, ActiveManager
from finance.services.plaid_api import PlaidApi
from .transfer_calculation import TransferCalculation

logger = logging.getLogger('app')


class TransactionManager(ActiveManager):
    @transaction.atomic
    def create_or_update_transactions(
            self, access_token, start_date=None, end_date=None):
        """
        1) Create new transactions.
        2) Or update transactions that already exists.
        3) Update accounts.
        """
        Account = apps.get_model('finance', 'Account')
        logger.debug(
            'Start to update transactions: {}'.format(access_token))
        Item = apps.get_model('finance', 'Item')
        item = Item.objects.get(access_token=access_token)

        logger.debug('Item: {}'.format(item.id))

        l = self.get_plaid_transactions(
            item, start_date=start_date, end_date=end_date)

        logger.debug('Number of transactions: {}'.format(len(l)))

        for tr in l:
            self.create_or_update_transaction(tr)

        # After updating transactions, update also accounts
        Account.objects.create_or_update_accounts(access_token)

    def create_or_update_transaction(self, api_response):
        """
        api_response is dictionary with response result.
        If transaction's account is deleted (is_active=False),
        do not process this transaction.
        """
        logger.debug('Start to create/update transaction')

        Account = apps.get_model('finance', 'Account')
        d = api_response

        account_plaid_id = d.pop('account_id')
        d['account'] = Account.objects.get(plaid_id=account_plaid_id)
        if not d['account'].is_active:
            return None
        d['plaid_id'] = d.pop('transaction_id')

        m_fields = self.model._meta.get_fields()
        m_fields = [f.name for f in m_fields]

        d = {k: v for (k, v) in d.items() if k in m_fields}

        try:
            tr = self.model.objects.get(plaid_id=d['plaid_id'])
            tr.__dict__.update(d)
            logger.debug('Transaction updated')
        except self.model.DoesNotExist:
            tr = self.model(**d)
            logger.debug('Transaction created')
        tr.save()

        return tr

    def get_plaid_transactions(self, item, start_date=None, end_date=None):
        """
        Queries Plaid API for items's transactions.
        start_date and end_date: datetime.date objects.
        """
        if start_date is None:
            start_date = datetime.date.today() - datetime.timedelta(days=14)

        if end_date is None:
            end_date = datetime.date.today()

        pa = PlaidApi()
        return pa.get_transactions(
            item.access_token, start_date=start_date, end_date=end_date)


class Transaction(ActiveModel):
    """
    On save signal calculate and save roundup, but if roundup
    already has been processed (is_processed), then skip saving
    roundup even if transaction amount has been changed.
    """
    account = models.ForeignKey('Account', related_name='transactions')
    guid = models.CharField(max_length=100, unique=True)
    plaid_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=None)
    date = models.DateField(null=True, default=None)
    name = models.CharField(
        max_length=255, null=True, default=None)
    transaction_type = models.CharField(
        max_length=50, null=True, default=None)
    category = JSONField(null=True, default=None)
    category_id = models.CharField(max_length=100, null=True, default=None)
    pending = models.BooleanField(default=False)
    pending_transaction_id = models.CharField(
        max_length=255, null=True, default=None)
    payment_meta = JSONField(null=True, default=None)
    location = JSONField(null=True, default=None)
    roundup = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, default=None,
        help_text='Internal field. "Roundup" amount.')
    is_processed = models.NullBooleanField(
        default=False,
        help_text='Internal flag. Roundup has been applied')
    transfer_calculation = models.ForeignKey(TransferCalculation,
                                             related_name='transactions',
                                             blank=True, null=True,
                                             default=None)
    objects = TransactionManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'transaction'
        verbose_name_plural = 'transactions'
        ordering = ['-date']

    def __str__(self):
        return self.guid

    def calculate_roundup(self, value):
        """
        Do not apply roundups for transactions,
        which date less than user's signup date.
        """
        # Roundup only expense.
        # Expense come with "+"
        # Debit comes with "-"
        if value <= 0:
            return 0

        value = abs(value)

        top = math.ceil(float(value))
        roundup = top - value
        if roundup == 0:
            if not self.account.item.user.is_even_roundup:
                return 0
            elif value > 0:
                return 1
        return roundup

    def save(self, *args, **kwargs):
        Account = apps.get_model('finance', 'Account')
        TransferCalculation = apps.get_model('finance',
                                             'TransferCalculation')

        if not self.pk:
            self.guid = uuid.uuid4().hex

        if self.account.type in Account.ROUNDUP_TYPES and not self.is_processed:
            self.roundup = self.calculate_roundup(self.amount)

        if self.account.type not in Account.ROUNDUP_TYPES:
            self.is_processed = None

        user = self.account.item.user
        if self.transfer_calculation is None:
            tr_calc, created = TransferCalculation.objects.get_or_create(
                user=user
            )

            self.transfer_calculation = tr_calc
            tr_calc.save(self.roundup, self)

        super().save(*args, **kwargs)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'plaid_id',
        'account',
        'amount',
        'roundup',
        'name',
        'category',
        'transfer_calculation',
    )
    list_filter = ('account',)
    list_per_page = 500

    readonly_fields = (
        'account',
        'guid',
        'plaid_id',
        'amount',
        # 'date',
        'name',
        'transaction_type',
        'category',
        'category_id',
        'pending',
        'pending_transaction_id',
        'payment_meta',
        'location',
        'roundup',
        'is_processed'
    )

    def has_delete_permission(self, request, obj=None):
        return False
