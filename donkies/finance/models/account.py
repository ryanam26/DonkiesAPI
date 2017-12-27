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
from finance.models.item import Item

class AccountManager(ActiveManager):
    @transaction.atomic
    def create_or_update_accounts(self, context, user=None):
        """
        Input: api response from plaid API.
        """
        Item = apps.get_model('finance', 'Item')
        pa = PlaidApi()

        try:
            api_data = pa.get_accounts(context['access_token'])
        except Exception as e:
            raise e

        accounts = api_data['accounts']

        for d in accounts:
            try:
                self.create_or_update_account(
                    context['access_token'], d, user, context)
            except Exception as e:
                print(e)

    def create_or_update_account(self, access_token, data, user, context):
        """
        data is dictionary with response result.
        If account is deleted in Donkies (is_active=False), do not process.
        """
        from finance.services.dwolla_api import DwollaAPI

        m_fields = self.model._meta.get_fields()
        m_fields = [f.name for f in m_fields]

        d = {k: v for (k, v) in data.items() if k in m_fields}
        d['plaid_id'] = data['account_id']

        try:
            acc = self.model.objects.get(plaid_id=d['plaid_id'])
            if not acc.is_active:
                return None
            acc.__dict__.update(d)
        except self.model.DoesNotExist:
            acc = self.model(**d)

        if user is not None:
            try:
                funding_data = self.create_account_funding_source(
                    data, context['access_token'], user
                )
                item = Item.objects.create_item(user, context)
                acc.item = item
            except Exception as e:
                raise e

            if funding_data is not None:

                dw = DwollaAPI()

                dw.save_funding_source(
                    item,
                    user,
                    funding_data['funding_source'],
                    funding_data['dwolla_balance_id']
                )

                acc.is_funding_source_for_transfer = True

        if context.get('account_id') == data.get('account_id'):
            acc.is_primary = True

        acc.save()

        return acc

    def create_account_funding_source(self, account, access_token, user):
        from finance.services.dwolla_api import DwollaAPI

        searching_customer = user
        searching_type = 'checking'

        if user.is_parent:
            searching_customer = user.childs.first()
            searching_type = 'savings'

        if account['subtype'] == searching_type:
            dw = DwollaAPI()
            pa = PlaidApi()
            processor_token = pa.create_dwolla_processor_token(
                access_token,
                account['account_id'])

            try:
                fs = dw.create_dwolla_funding_source(
                    user, processor_token
                )
            except Exception as e:
                raise e

            Customer = apps.get_model('bank', 'Customer')
            customer = Customer.objects.get(user=searching_customer)

            customer_url = '{}customers/{}'.format(
                dw.get_api_url(), customer.dwolla_id
            )
            funding_sources = dw.app_token.get(
                '%s/funding-sources' % customer_url
            )
            dwolla_balance_id = None

            for i in funding_sources.body['_embedded']['funding-sources']:
                if 'type' in i and i['type'] == 'balance':
                    dwolla_balance_id = i['id']

            return {
                "funding_source": fs,
                "dwolla_balance_id": dwolla_balance_id
            }

        return None

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
        """
        account = self.model.objects.get(
            id=account_id, type_ds=self.model.DEBIT)

        self.model.objects.active().filter(
            item__user=account.item.user)\
            .update(is_funding_source_for_transfer=False)
        account.is_funding_source_for_transfer = True
        account.save()
        return account

    @transaction.atomic
    def set_primary(self, account_id):
        """
        Set primary account (debit account or credit card).
        """
        account = self.model.objects.get(
            id=account_id, type__in=self.model.ROUNDUP_TYPES)

        self.model.objects.active().filter(
            item__user=account.item.user)\
            .update(is_primary=False)
        account.is_primary = True
        account.save()
        return account

    @transaction.atomic
    def set_funding_source_dwolla(self, account_id):
        """
        Dwolla implementation.
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

    def create_manual_account(
            self, user_id, institution_id, account_number,
            additional_info):
        """
        If Item (institution) already exists for manual account
        and user adds other debt account for the same institution,
        do not create additional Item (use existing).
        """
        User = apps.get_model('web', 'User')
        Item = apps.get_model('finance', 'Item')
        Institution = apps.get_model('finance', 'Institution')

        user = User.objects.get(id=user_id)
        institution = Institution.objects.get(
            id=institution_id, is_manual=True)

        try:
            item = Item.objects.get(user=user, institution=institution)
        except Item.DoesNotExist:
            item = Item(user=user, institution=institution)
            item.save()

        account = self.model(
            name=institution.name,
            type=self.model.CREDIT,
            item=item,
            account_number=account_number,
            additional_info=additional_info)
        account.save()
        return account


class Account(ActiveModel):
    """
    type - Plaid type.
    type_ds - Donkies type.

    Accounts can be created by Plaid or manually.
    Manual account doesn't have plaid_id.
    Manual account has internal Item that doesn't exist
    in Plaid.

    When user creates manual account, we automatically create
    Item for that account.
    """
    DEPOSITORY = 'depository'
    CREDIT = 'credit'
    LOAN = 'loan'
    MORTGAGE = 'mortgage'
    BROKERAGE = 'brokerage'
    OTHER = 'other'

    DEBIT_TYPES = [DEPOSITORY]
    DEBT_TYPES = [CREDIT, LOAN, MORTGAGE]
    ROUNDUP_TYPES = [DEPOSITORY, CREDIT]

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
    plaid_id = models.CharField(
        max_length=255, null=True, default=None, blank=True,
        help_text='None for manual accounts.')
    name = models.CharField(
        max_length=255,
        help_text='Set by user or institution')
    official_name = models.CharField(
        max_length=255, null=True, default=None, blank=True,
        help_text='The official name given by the financial institution.')
    balance = models.IntegerField(null=True, default=None, blank=True)
    balances = JSONField(null=True, default=None)
    mask = models.CharField(
        max_length=4, null=True, default=None, blank=True,
        help_text='Last 4 digits of account number')
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
    is_primary = models.BooleanField(default=False)
    account_number = models.CharField(
        max_length=100, null=True, default=None, blank=True)
    routing_number = models.CharField(
        max_length=100, null=True, default=None, blank=True)
    wire_routing = models.CharField(
        max_length=100, null=True, default=None, blank=True)
    additional_info = models.CharField(
        max_length=500, null=True, default=None, blank=True,
        help_text='Used for manual debt accounts.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, default=None)
    pause = models.BooleanField(default=False, blank=True)

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
        Dwolla integration.
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

    def get_ds_type(self):
        if self.type in self.DEBIT_TYPES:
            return self.DEBIT
        if self.type in self.DEBT_TYPES:
            return self.DEBT
        return self.OTHER

    def get_stripe_token(self):
        """
        One-time Stripe's token.
        Used to create Charge in Stripe.
        """
        pa = PlaidApi()
        return pa.get_stripe_token(
            self.item.access_token, self.plaid_id)

    def set_account_numbers(self):
        """
        Request to Plaid API and set account_number
        and routing_number for account.
        """
        pa = PlaidApi()
        d = pa.get_accounts_info(self.item.access_token)
        for dic in d['numbers']:
            if dic['account_id'] == self.plaid_id:
                self.account_number = dic['account']
                self.routing_number = dic['routing']
                self.save()

    def pause_on(self, *args, **kwargs):
        self.pause = True
        self.save()

    def pause_off(self, *args, **kwargs):
        self.pause = False
        self.save()

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

    @staticmethod
    def get_admin_urls():
        return [
            (r'^custom/fetch_account_numbers/(?P<account_id>\d+)/$',
             'fetch_account_numbers_view'),
        ]


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


@receiver(post_save, sender=Account)
def make_funding_source(sender, instance, created, **kwargs):
    """
    If user adds first debit account, make it automatically
    as funding source.
    """
    if instance.type_ds == Account.DEBIT:
        qs = Account.objects.active().filter(
            item__user=instance.item.user, type_ds=Account.DEBIT)
        if qs.count() == 1:
            Account.objects.active().filter(
                id=instance.id).update(is_funding_source_for_transfer=True)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'official_name',
        'balance',
        'type',
        'type_ds',
        'subtype',
        'show_account_number',
        'routing_number',
        'is_active',
        'plaid_id',
        'pause',
    )
    readonly_fields = (
        'item',
        'guid',
        'name',
        'official_name',
        'balances',
        'mask',
        'subtype',
        'type',
        'type_ds',
        'transfer_share',
        'is_funding_source_for_transfer',
        'is_primary',
        'account_number',
        'routing_number',
        'wire_routing',
        'created_at',
        'updated_at'
    )

    def get_queryset(self, request):
        qs = super(AccountAdmin, self).get_queryset(request)
        return qs.filter(is_active=True)

    def show_account_number(self, obj):
        print(obj.account_number)
        if obj.account_number:
            return obj.account_number

        href = '/admin/custom/fetch_account_numbers/{}/'.format(obj.id)
        link = '<a href="{}">fetch</a>'.format(href)
        return link
    show_account_number.short_description = 'account number'
    show_account_number.allow_tags = True
