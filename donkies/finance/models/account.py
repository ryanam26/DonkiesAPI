import uuid
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib import admin
from django.apps import apps
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.fields import JSONField
from web.models import ActiveModel, ActiveManager
from finance.services.plaid_api import PlaidApi


class AccountManager(ActiveManager):
    @transaction.atomic
    def create_or_update_accounts(self, access_token):
        """
        Input: api response from plaid API.
        """
        Item = apps.get_model('finance', 'Item')

        pa = PlaidApi()
        api_data = pa.get_accounts(access_token)

        accounts = api_data['accounts']
        item = Item.objects.get(plaid_id=api_data['item']['item_id'])
        for d in accounts:
            self.create_or_update_account(item, d)

    def create_or_update_account(self, item, data):
        """
        data is dictionary with response result.
        If account is deleted in Donkies (is_active=False), do not process.
        """
        m_fields = self.model._meta.get_fields()
        m_fields = [f.name for f in m_fields]

        d = {k: v for (k, v) in data.items() if k in m_fields}
        d['item'] = item
        d['plaid_id'] = data['account_id']

        try:
            acc = self.model.objects.get(plaid_id=d['plaid_id'])
            if not acc.is_active:
                return None
            acc.__dict__.update(d)
        except self.model.DoesNotExist:
            acc = self.model(**d)
        acc.save()
        return acc

    def get_plaid_accounts(self, access_token):
        pa = PlaidApi()
        d = pa.get_accounts(access_token)
        return d['accounts']

    def debit_accounts(self):
        return self.model.objects.active().filter(type_ds=self.model.DEBIT)

    def debt_accounts(self):
        return self.model.objects.active().filter(type_ds=self.model.DEBT)

    @transaction.atomic
    def set_funding_source(self, account_id):
        """
        Set debit account as funding source for user.
        Account should exist in FundingSource.
        """
        FundingSource = apps.get_model('bank', 'FundingSource')
        account = self.model.objects.get(
            id=account_id, type_ds=self.model.DEBIT)

        if not FundingSource.objects.filter(account=account).exists():
            message = 'Attempt to set "is_funding_source_for_transfer" '
            message += 'for account that not exists in bank.FundingSource.'
            raise ValidationError(message)

        self.model.objects.active().filter(
            item__user=account.item.user)\
            .update(is_funding_source_for_transfer=False)
        account.is_funding_source_for_transfer = True
        account.save()
        return account

    def set_account_number(self, account_id, account_number):
        """
        Can set account only if didn't set before.
        Used for debt accounts.
        """
        account = self.model.objects.get(id=account_id)
        if account.account_number is not None:
            raise ValidationError('Account number was set earlier.')

        account.account_number = account_number
        account.save()

    @transaction.atomic
    def change_active(self, account_id, is_active):
        """
        is_active = True - besides account itself,
                    activates also all transactions.
        is_active = False - besides account itself,
                    deactivates also all transactions.
        """
        Transaction = apps.get_model('finance', 'Transaction')
        self.model.objects.filter(id=account_id)\
            .update(is_active=is_active)
        Transaction.objects.filter(account_id=account_id)\
            .update(is_active=is_active)


"""
CALL to account info endpoint to get account numbers
pa.get_accounts_info
Not implemented yet

{
    'name': 'Plaid Checking',
    'account_id': 'doQrm45pBRT8315WlRqzua7aoAd3xWHJgapQK',
    'type': 'depository',
    'official_name': 'Plaid Gold Standard 0% Interest Checking',
    'subtype': 'checking',
    'balances': {
        'available': 100,
        'limit': None,
        'current': 110
        },
    'mask': '0000'
    }, 

    'item': {
    'webhook': 'https://example.com/webhook',
    'error': None,
    'available_products': ['balance'],
    'item_id': '6aK79r8z5ktGNL93AKvocA3p7Q3xm8hANRNJo',
    'institution_id': 'ins_109509',
    'billed_products': ['auth', 'transactions']
},

    'numbers': [
    {'account': '1111222233330000',
    'routing': '011401533',
    'account_id': 'doQrm45pBRT8315WlRqzua7aoAd3xWHJgapQK',
    'wire_routing': '021000021'
    },
[

"""


class Account(ActiveModel):
    """
    type - Plaid type.
    type_ds - Donkies type.
    """
    DEPOSITORY = 'depository'
    CREDIT = 'credit'
    LOAN = 'loan'
    MORTGAGE = 'mortgage'
    BROKERAGE = 'brokerage'
    OTHER = 'other'

    DEBIT_TYPES = [DEPOSITORY]
    DEBT_TYPES = [CREDIT, LOAN, MORTGAGE]

    TYPE_CHOICES = (
        (DEPOSITORY, 'depository'),
        (CREDIT, 'credit'),
        (LOAN, 'loan'),
        (MORTGAGE, 'mortgage'),
        (BROKERAGE, 'brokerage'),
        (OTHER, 'other'),
    )

    DEBIT = 'debit'
    DEBT = 'debt'

    TYPE_DS_CHOICES = (
        (DEBIT, 'debit'),
        (DEBT, 'debt'),
        (OTHER, 'other'))

    item = models.ForeignKey('Item', related_name='accounts')
    guid = models.CharField(max_length=100, unique=True)
    plaid_id = models.CharField(max_length=255)
    name = models.CharField(
        max_length=255,
        help_text='Set by user or institution')
    official_name = models.CharField(
        max_length=255,
        help_text='The official name given by the financial institution.')
    balance = models.IntegerField(null=True, default=None, blank=True)
    balances = JSONField(null=True, default=None)
    mask = models.CharField(
        max_length=4, help_text='Last 4 digits of account number')
    subtype = models.CharField(
        max_length=255, null=True, default=None, choices=TYPE_CHOICES)
    type = models.CharField(
        max_length=100, null=True, default=None, choices=TYPE_CHOICES)
    type_ds = models.CharField(
        max_length=15,
        help_text='Internal type',
        choices=TYPE_DS_CHOICES,
        default=OTHER)
    transfer_share = models.IntegerField(
        default=0,
        help_text=(
            'For debt accounts in percentage. '
            'Share of transfer amount between debt accounts.'
            'The total share of all accounts should be 100%.'
        )
    )
    is_funding_source_for_transfer = models.BooleanField(
        default=False,
        help_text='For debit account. Funding source for transfer.')
    account_number = models.CharField(
        max_length=100, null=True, default=None, blank=True)
    routing_number = models.CharField(
        max_length=100, null=True, default=None, blank=True)
    wire_routing = models.CharField(
        max_length=100, null=True, default=None, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, default=None)

    objects = AccountManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'account'
        verbose_name_plural = 'accounts'
        ordering = ['type_ds', 'item', 'name']

    def __str__(self):
        name = self.name or 'No name'
        return '{}: ({})'.format(name, self.item.user.email)

    @property
    def funding_source(self):
        """
        Returns associated funding source or None.
        """
        FundingSource = apps.get_model('bank', 'FundingSource')
        return FundingSource.objects.filter(account=self).first()

    def get_balance(self):
        """
        Balance come from API as object:
        'balances': {
            'available': 100,
            'limit': None,
            'current': 110
        }
        Index value to database.
        """
        if self.balances is None:
            return None
        return self.balances.get('current', None)

    @property
    def is_dwolla_created(self):
        fs = self.funding_source
        if fs is None:
            return False
        if fs.dwolla_id is None:
            return False
        return True

    def save(self, *args, **kwargs):
        """
        Assume that account can not change type.
        For example: debt account can not be debit.
        """
        if not self.pk:
            self.type_ds = self.get_ds_type()
            self.guid = uuid.uuid4().hex

        self.balance = self.get_balance()
        super().save(*args, **kwargs)

    def get_ds_type(self):
        if self.type in self.DEBIT_TYPES:
            return self.DEBIT
        if self.type in self.DEBT_TYPES:
            return self.DEBT
        return self.OTHER


@receiver(post_save, sender=Account)
def apply_transfer_share(sender, instance, created, **kwargs):
    """
    If user adds first debt account, set transfer_share to 100%.
    """
    if instance.type_ds == Account.DEBT:
        qs = Account.objects.active().filter(
            item__user=instance.item.user, type_ds=Account.DEBT)
        if qs.count() == 1:
            Account.objects.active().filter(
                id=instance.id).update(transfer_share=100)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'official_name',
        'type',
        'type_ds',
        'subtype',
        'guid',
        'plaid_id'
    )
    readonly_fields = (
        'item',
        'guid',
        'plaid_id',
        'name',
        'official_name',
        'balances',
        'mask',
        'subtype',
        'type',
        'type_ds',
        'transfer_share',
        'is_funding_source_for_transfer',
        'account_number',
        'routing_number',
        'wire_routing',
        'created_at',
        'updated_at'
    )

    def has_delete_permission(self, request, obj=None):
        return False
