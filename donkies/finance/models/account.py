import uuid
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib import admin
from finance.services.atrium_api import AtriumApi
from django.apps import apps
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from web.models import ActiveModel, ActiveManager


class AccountManager(ActiveManager):
    @transaction.atomic
    def create_or_update_accounts(self, user_guid, l):
        """
        Input: all user accounts from atrium API.

        TODO: pagination.
              Before passing accounts, should collect
              all of them for each user.
        """
        for acc in l:
            self.create_or_update_account(acc)

    def create_or_update_account(self, api_response):
        """
        api_response is dictionary with response result.
        If account is deleted in Donkies (is_active=False), do not process.
        """
        Member = apps.get_model('finance', 'Member')
        d = api_response
        d.pop('user_guid')
        d.pop('institution_code')
        d['member'] = Member.objects.get(guid=d.pop('member_guid'))

        m_fields = self.model._meta.get_fields()
        m_fields = [f.name for f in m_fields]

        d = {k: v for (k, v) in d.items() if k in m_fields}

        try:
            acc = self.model.objects.get(guid=d['guid'])
            if not acc.is_active:
                return None
            acc.__dict__.update(d)
        except self.model.DoesNotExist:
            acc = self.model(**d)
        acc.save()
        return acc

    def get_atrium_accounts(self, user_guid):
        """
        Queries atrium API for user's accounts.
        TODO: processing errors.
        """
        per_page = 100

        a = AtriumApi()
        res = a.get_accounts(user_guid, records_per_page=per_page)
        return res['accounts']

    def get_accounts(self, user_guid):
        """
        Returns user accounts from database.
        """
        return self.model.objects.active().filter(
            member__user__guid=user_guid)

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
            member__user=account.member.user)\
            .update(is_funding_source_for_transfer=False)
        account.is_funding_source_for_transfer = True
        account.save()
        return account

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


class Account(ActiveModel):
    """
    type - Atrium MX type.
    type_ds - Donkies type.
    """
    CHECKING = 'CHECKING'
    SAVINGS = 'SAVINGS'
    CASH = 'CASH'
    PREPAID = 'PREPAID'
    LOAN = 'LOAN'
    CREDIT_CARD = 'CREDIT_CARD'
    LINE_OF_CREDIT = 'LINE_OF_CREDIT'
    MORTGAGE = 'MORTGAGE'
    INVESTMENT = 'INVESTMENT'
    PROPERTY = 'PROPERTY'

    DEBIT_TYPES = (CHECKING, SAVINGS, CASH, PREPAID)
    DEBT_TYPES = (LOAN, CREDIT_CARD, LINE_OF_CREDIT, MORTGAGE)
    INVESTMENT_TYPES = (INVESTMENT, PROPERTY)

    DEBIT = 'debit'
    DEBT = 'debt'
    INVESTMENT = 'investment'
    OTHER = 'other'

    TYPE_DS_CHOICES = (
        (DEBIT, 'debit'),
        (DEBT, 'debt'),
        (INVESTMENT, 'investment'),
        (OTHER, 'other'))

    member = models.ForeignKey('Member', related_name='accounts')
    guid = models.CharField(max_length=100, unique=True)
    uid = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255, null=True, default=None)
    apr = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        help_text='Annual Percentage Rate.',
        null=True,
        default=None)
    apy = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        help_text='Annual Percentage Yield.',
        null=True,
        default=None)
    available_balance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        help_text='The current available account balance.',
        null=True,
        default=None)
    available_credit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='The current available credit balance of the account.',
        null=True,
        default=None)
    balance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        help_text='The current Account Balance.',
        null=True,
        default=None)
    created_at = models.DateTimeField(null=True, default=None)
    day_payment_is_due = models.IntegerField(null=True, default=None)
    is_closed = models.BooleanField(default=False)
    credit_limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='The credit limit for the account.',
        null=True,
        default=None)
    interest_rate = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        help_text='Interest rate, %',
        null=True,
        default=None)
    last_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Amount of the account\'s last payment.',
        null=True,
        default=None)
    last_payment_at = models.DateTimeField(null=True, default=None)
    matures_on = models.DateTimeField(null=True, default=None)
    minimum_balance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        help_text='Minimum required balance.',
        null=True,
        default=None)
    minimum_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Minimum payment.',
        null=True,
        default=None)
    original_balance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        help_text='Original balance.',
        null=True,
        default=None)
    payment_due_at = models.DateTimeField(null=True, default=None)
    payoff_balance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        help_text='Payoff Balance',
        null=True,
        default=None)
    started_on = models.DateTimeField(null=True, default=None)
    subtype = models.CharField(max_length=255, null=True, default=None)
    total_account_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        help_text='The total value of the account.',
        null=True,
        default=None)
    type = models.CharField(max_length=100, null=True, default=None)
    type_ds = models.CharField(
        max_length=15,
        help_text='Internal type',
        choices=TYPE_DS_CHOICES,
        default=OTHER)
    updated_at = models.DateTimeField(null=True, default=None)
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

    objects = AccountManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'account'
        verbose_name_plural = 'accounts'
        ordering = ['type_ds', 'member']

    def __str__(self):
        s = self.member.name
        if self.name:
            s += ' {}'.format(self.name)
        s += ' ({})'.format(self.member.user.email)
        return s

    @property
    def funding_source(self):
        """
        Returns associated funding source or None.
        """
        FundingSource = apps.get_model('bank', 'FundingSource')
        return FundingSource.objects.filter(account=self).first()

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
        If account can change type: TODO handle this.
        """
        if not self.pk:
            self.type_ds = self.get_ds_type()
            self.uid = uuid.uuid4().hex
        super().save(*args, **kwargs)

    def get_ds_type(self):
        if self.type in self.DEBIT_TYPES:
            return self.DEBIT
        if self.type in self.DEBT_TYPES:
            return self.DEBT
        if self.type in self.INVESTMENT_TYPES:
            return self.INVESTMENT
        return self.OTHER


@receiver(post_save, sender=Account)
def apply_transfer_share(sender, instance, created, **kwargs):
    """
    If user adds first debt account, set transfer_share to 100%.
    """
    if instance.type_ds == Account.DEBT:
        qs = Account.objects.active().filter(
            member__user=instance.member.user, type_ds=Account.DEBT)
        if qs.count() == 1:
            Account.objects.active().filter(
                id=instance.id).update(transfer_share=100)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'type_ds',
        'guid',
        'available_balance',
        'available_credit',
        'balance',
        'credit_limit',
        'original_balance',
        'payoff_balance'
    )

    def has_delete_permission(self, request, obj=None):
        return False
