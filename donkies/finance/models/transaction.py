import datetime
import math
import uuid
from django.db import models
from django.contrib import admin
from django.apps import apps
from django.utils import timezone
from django.db import transaction
from finance.services.atrium_api import AtriumApi


class TransactionManager(models.Manager):
    @transaction.atomic
    def create_transactions(self, user_guid, l):
        """
        Input: all user transactions from atrium API.

        1) Create new transactions.
        2) Or update transactions that already exists and
            updated_at less that 2 weeks ago.


        TODO: pagination.
              Before passing accounts, should collect
              all of them for each user.
        """
        for tr in l:
            self.create_or_update_transaction(tr)

    def create_or_update_transaction(self, api_response):
        """
        api_response is dictionary with response result.
        """
        Account = apps.get_model('finance', 'Account')
        d = api_response

        d.pop('user_guid')
        d.pop('member_guid')
        d['account'] = Account.objects.get(guid=d.pop('account_guid'))

        try:
            dt = timezone.now() - datetime.timedelta(days=14)
            tr = self.model.objects.get(guid=d['guid'])
            if tr.updated_at < dt:
                return tr
            tr.__dict__.update(d)
        except self.model.DoesNotExist:
            tr = self.model(**d)
        tr.save()
        return tr

    def get_atrium_transactions(self, user_guid):
        """
        Queries atrium API for user's transactions.
        TODO: processing errors.
        """
        a = AtriumApi()
        return a.get_transactions(user_guid)

    def get_transactions(self, user_guid):
        """
        Returns transactions from database.
        """
        return self.model.objects.filter(
            account__member__user__guid=user_guid)


class Transaction(models.Model):
    account = models.ForeignKey('Account')
    guid = models.CharField(max_length=100, unique=True)
    uid = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, default=None)
    check_number = models.IntegerField(null=True, default=None)
    category = models.CharField(max_length=255, null=True, default=None)
    created_at = models.DateTimeField(null=True, default=None)
    date = models.DateField(null=True, default=None)
    description = models.CharField(max_length=3000, null=True, default=None)
    is_bill_pay = models.NullBooleanField()
    is_direct_deposit = models.NullBooleanField()
    is_expense = models.NullBooleanField()
    is_fee = models.NullBooleanField()
    is_income = models.NullBooleanField()
    is_overdraft_fee = models.NullBooleanField()
    is_payroll_advance = models.NullBooleanField()
    is_processed = models.BooleanField(
        default=False,
        help_text='Internal flag. Change has been transferred to debt account')
    latitude = models.DecimalField(
        max_digits=10, decimal_places=6, null=True, default=None)
    longitude = models.DecimalField(
        max_digits=10, decimal_places=6, null=True, default=None)
    memo = models.CharField(max_length=255, null=True, default=None)
    merchant_category_code = models.IntegerField(null=True, default=None)
    original_description = models.CharField(
        max_length=3000, null=True, default=None)
    posted_at = models.DateTimeField(null=True, default=None)
    roundup = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, default=None,
        help_text='Internal field. "Change" amount.')
    status = models.CharField(max_length=50)
    top_level_category = models.CharField(
        max_length=255, null=True, default=None)
    transacted_at = models.DateTimeField(null=True, default=None)
    type = models.CharField(max_length=50)
    updated_at = models.DateTimeField(null=True, default=None)

    objects = TransactionManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'transaction'
        verbose_name_plural = 'transactions'
        ordering = ['account']

    def __str__(self):
        return self.uid

    def calculate_roundup(self, value):
        top = math.ceil(value)
        return top - value

    def save(self, *args, **kwargs):
        Account = apps.get_model('finance', 'Account')
        if not self.pk:
            self.uid = uuid.uuid4().hex

        if self.account.type_ds == Account.DEBIT:
            self.roundup = self.calculate_roundup(self.amount)
        super().save(*args, **kwargs)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    pass
