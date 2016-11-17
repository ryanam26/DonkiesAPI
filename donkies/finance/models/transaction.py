import math
import uuid
from django.db import models
from django.contrib import admin
from django.apps import apps
from django.db import transaction
from finance.services.atrium_api import AtriumApi


class TransactionManager(models.Manager):
    @transaction.atomic
    def create_transactions(self, user_guid, l):
        """
        Input: all user transactions from atrium API.

        Atrium API is source of truth.
        Remove all user's transactions from db,
        before inserting all transactions.

        It is better for performance, than update each particular
        transaction.

        TODO: pagination.
              Before passing accounts, should collect
              all of them for each user.
        """
        self.model.objects.filter(
            account__member__user__guid=user_guid).delete()
        for tr in l:
            self.create_transaction(tr)

    def create_transaction(self, api_response):
        """
        api_response is dictionary with response result.
        """
        Account = apps.get_model('finance', 'Account')
        d = api_response
        d.pop('user_guid')
        d.pop('member_guid')
        d['account'] = Account.objects.get(guid=d.pop('account_guid'))
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
        max_digits=5, decimal_places=2, null=True, default=None)
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
        if not self.pk:
            self.uid = uuid.uuid4().hex

        self.roundup = self.calculate_roundup(self.amount)
        super().save(*args, **kwargs)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    pass
