import datetime
import math
import uuid
import time
from django.db import models
from django.contrib import admin
from django.apps import apps
from django.utils import timezone
from django.db import transaction
from finance.services.atrium_api import AtriumApi
from web.models import ActiveModel, ActiveManager


class TransactionManager(ActiveManager):
    @transaction.atomic
    def create_or_update_transactions(self, user_guid, l):
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
            print(tr)
            self.create_or_update_transaction(tr)

    def create_or_update_transaction(self, api_response):
        """
        api_response is dictionary with response result.
        If transaction's account is deleted (is_active=False),
        do not process this transaction.
        """
        Account = apps.get_model('finance', 'Account')
        d = api_response

        d.pop('user_guid', None)
        d.pop('member_guid', None)
        d['account'] = Account.objects.get(guid=d.pop('account_guid'))
        if not d['account'].is_active:
            return None

        m_fields = self.model._meta.get_fields()
        m_fields = [f.name for f in m_fields]

        d = {k: v for (k, v) in d.items() if k in m_fields}

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

    def get_atrium_transactions(self, user_guid, from_date=None, to_date=None):
        """
        Queries atrium API for user's transactions.
        from_date and to_date: datetime.date objects.
        TODO: processing errors.
        """
        page = 1
        per_page = 100

        today = datetime.date.today()
        if from_date is None:
            from_date = today - datetime.timedelta(days=14)

        if to_date is None:
            to_date = today

        from_date = from_date.strftime('%Y-%m-%d')
        to_date = to_date.strftime('%Y-%m-%d')

        l = []

        while True:
            time.sleep(0.5)

            a = AtriumApi()
            res = a.get_transactions(
                user_guid,
                from_date=from_date,
                to_date=to_date,
                records_per_page=per_page,
                page=page)

            l += res['transactions']
            if res['pagination']['total_pages'] <= page:
                break
            page += 1

        return l

    def get_transactions(self, user_guid):
        """
        Returns transactions from database.
        """
        return self.model.objects.active().filter(
            account__member__user__guid=user_guid)


class Transaction(ActiveModel):
    """
    On save signal calculate and save roundup, but if roundup
    already has been processed (is_processed), then skip saving
    roundup even if transaction amount has been changed.
    """
    account = models.ForeignKey('Account', related_name='transactions')
    guid = models.CharField(max_length=100, unique=True)
    uid = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=None)
    check_number = models.IntegerField(null=True, default=None)
    check_number_string = models.CharField(
        max_length=255, null=True, default=None, blank=True)
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
    status = models.CharField(max_length=50)
    top_level_category = models.CharField(
        max_length=255, null=True, default=None)
    transacted_at = models.DateTimeField(null=True, default=None)
    type = models.CharField(max_length=50)
    updated_at = models.DateTimeField(null=True, default=None)
    roundup = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, default=None,
        help_text='Internal field. "Change" amount.')
    is_processed = models.NullBooleanField(
        default=False,
        help_text='Internal flag. Roundup has been transferred')

    objects = TransactionManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'transaction'
        verbose_name_plural = 'transactions'
        ordering = ['account', '-transacted_at']

    def __str__(self):
        return self.uid

    def calculate_roundup(self, value):
        top = math.ceil(float(value))
        return top - value

    def save(self, *args, **kwargs):
        Account = apps.get_model('finance', 'Account')
        if not self.pk:
            self.uid = uuid.uuid4().hex

        if self.account.type_ds == Account.DEBIT and not self.is_processed:
            self.roundup = self.calculate_roundup(self.amount)

        if self.account.type_ds != Account.DEBIT:
            self.is_processed = None

        super().save(*args, **kwargs)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'account',
        'status',
        'amount',
        'roundup',
        'is_expense',
        'category',
        'description',
    )
    list_filter = ('account',)

    def has_delete_permission(self, request, obj=None):
        return False
