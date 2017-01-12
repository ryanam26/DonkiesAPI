import uuid
from django.db import models
from django.contrib import admin
from finance.services.atrium_api import AtriumApi
from django.apps import apps
from django.db import transaction
from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.dispatch import receiver


class AccountManager(models.Manager):
    @transaction.atomic
    def create_accounts(self, user_guid, l):
        """
        Input: all user accounts from atrium API.

        TODO: pagination.
              Before passing accounts, should collect
              all of them for each user.
        """
        self.model.objects.filter(member__user__guid=user_guid).delete()
        for acc in l:
            self.create_or_update_account(acc)

    def create_or_update_account(self, api_response):
        """
        api_response is dictionary with response result.
        """
        Member = apps.get_model('finance', 'Member')
        d = api_response
        d.pop('user_guid')
        d.pop('institution_code')
        d['member'] = Member.objects.get(guid=d.pop('member_guid'))

        try:
            acc = self.model.objects.get(guid=d['guid'])
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
        a = AtriumApi()
        return a.get_accounts(user_guid)

    def get_accounts(self, user_guid):
        """
        Returns user accounts from database.
        """
        return self.model.objects.filter(
            member__user__guid=user_guid)

    def debit_accounts(self):
        return self.model.objects.filter(type_ds=self.model.DEBIT)

    def debt_accounts(self):
        return self.model.objects.filter(type_ds=self.model.DEBT)


class Account(models.Model):
    """
    type - Atrium MX type.
    type_ds - Donkies type.
    """
    CHECKING = 'CHECKING'
    SAVINGS = 'SAVINGS'
    CASH = 'CASH'
    PREPAID = 'PREPAID'
    LOAN = 'LOAN'
    CREDIT_CARD = 'CREDIT CARD'
    LINE_OF_CREDIT = 'LINE OF CREDIT'
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

    member = models.ForeignKey('Member')
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

    objects = AccountManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'account'
        verbose_name_plural = 'accounts'
        ordering = ['type_ds', 'member']

    def __str__(self):
        if self.name:
            return self.name
        return self.uid

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
        qs = Account.objects.filter(
            member__user=instance.member.user, type_ds=Account.DEBT)
        if qs.count() == 1:
            Account.objects.filter(id=instance.id).update(transfer_share=100)


# Got error with multiple accounts in generator "clean".

# @receiver(post_delete, sender=Account)
# def delete_account(sender, instance, **kwargs):
#     """
#     If account's member connected only to this account,
#     remove member also.
#     """
#     Member = apps.get_model('finance', 'Member')
#     qs = Account.objects.filter(member_id=instance.member.id)
#     if qs.count() == 0:
#         member = Member.objects.get(id=instance.member.id)
#         member.delete()


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    pass
