"""
Transfer flow to TransferStripe model.

1) TransferStripe.objects.process_prepare
   On the last day of the month, all user's roundup collected
   in TransferPrepare model - send to Stripe. We create Charge
   object with collected amount and save all data to TransferStripe
   model. All collected TransferPrepare are marked as processed
   (is_processed=True, processed_at=now)

2) Periodic Celery task "update_stripe_transfers" look for all
   transfers with status=pending and fetch new info about them from Stripe.
   (in future can be chaged to Stripe's webhook).
   Update status and all corresponding Charge's fields.
"""

import datetime
from django.db import transaction
from django.utils import timezone
from django.apps import apps
from django.db.models import Sum
from django.db import models
from django.contrib import admin
from django.contrib.postgres.fields import JSONField


class TransferStripeManager(models.Manager):
    def create_charge(self, account, stripe_charge):
        """
        stripe_charge - Stripe's API charge dict like object.
        """
        d = stripe_charge
        charge = self.model(account=account)

        dt = datetime.datetime.fromtimestamp(d.pop('created'))
        charge.created_at = timezone.make_aware(dt)
        charge.stripe_id = d.pop('id')
        charge.amount_stripe = d.pop('amount')

        fields = (
            'status', 'balance_transaction', 'currency',
            'captured', 'description', 'failure_code', 'livemode',
            'metadata', 'paid', 'source')

        for key in fields:
            setattr(charge, key, d[key])

        charge.save()
        return charge

    def process_prepare(self):
        """
        Called by celery scheduled task.
        Process TransferPrepare to TransferStripe model.
        Create Charge on Stripe.
        """
        TransferPrepare = apps.get_model('finance', 'TransferPrepare')

        users = TransferPrepare.objects.filter(is_processed=False)\
            .order_by('account__item__user_id')\
            .values_list('account__item__user_id', flat=True)\
            .distinct()

        for user_id in users:
            self.charge_user(user_id)

    @transaction.atomic
    def charge_user(self, user_id):
        TransferPrepare = apps.get_model('finance', 'TransferPrepare')
        User = apps.get_model('web', 'User')

        user = User.objects.get(id=user_id)
        fs = user.get_funding_source_account()

        amount = TransferPrepare.objects.filter(
            is_processed=False,
            account__item__user=user)\
            .aggregate(Sum('roundup'))['roundup__sum']

        # Create charge in Stripe for that amount

        



        TransferPrepare.objects.filter(
            is_processed=False,
            account__item__user=user).update(is_processed=True)

        tds = self.model(account=fs, amount=sum)
        tds.save()

    
    

   

   

    def get_date_queryset(self, is_date_filter=True):
        """
        Returns queryset for available payments.
        """
        filters = dict(
            is_processed_to_user=False,
            is_sent=True
        )
        if is_date_filter:
            filters['sent_at__lt'] = self.get_date()
        return self.model.objects.filter(**filters)

    def get_user_queryset(self, user_id, is_date_filter=True):
        """
        Returns queryset for available payments
        for particular user.

        If is_date_filter is False, get all available payments
        (do not filter by date)
        """
        return self.get_date_queryset(is_date_filter=is_date_filter).filter(
            account__item__user_id=user_id)

    def get_date(self):
        """
        Returns date, for filter TransferDonkies that less
        than that date.

        If today's date is less than 15th, returns 1st day of last month.
        If today's date is more or equal 15th, returns
        1st day of current month.
        """
        today = timezone.now().replace(
            hour=0, minute=0, second=0, microsecond=0)
        if today.day < 15:
            dt = today.replace(day=1) - datetime.timedelta(days=1)
            return dt.replace(day=1)
        return today.replace(day=1)


class TransferStripe(models.Model):
    PENDING = 'pending'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'

    STATUS_CHOICES = (
        (PENDING, PENDING),
        (SUCCEEDED, SUCCEEDED),
        (FAILED, FAILED),
    )

    account = models.ForeignKey('finance.Account', related_name='charges')
    # Stripe fields (get from Charge object)
    stripe_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(
        max_length=9, default=PENDING, choices=STATUS_CHOICES)
    amount_stripe = models.IntegerField(help_text='Amount in cents.')
    balance_transaction = models.CharField(
        max_length=100, null=True, default=None, blank=True)
    currency = models.CharField(max_length=3, default='usd')
    captured = models.BooleanField(default=True)
    description = models.CharField(
        max_length=255, null=True, default=None, blank=True)
    failure_code = models.CharField(
        max_length=100, null=True, default=None, blank=True)
    failure_message = models.CharField(
        max_length=100, null=True, default=None, blank=True)
    livemode = models.BooleanField(default=False)
    metadata = JSONField(null=True, default=None)
    paid = models.BooleanField(default=False)
    source = JSONField(null=True, default=None)
    created_at = models.DateTimeField(null=True, default=None)
    # Other fields
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_processed_to_user = models.BooleanField(
        default=False, help_text='Funds processed to TransferUser model.')
    processed_at = models.DateTimeField(null=True, default=None, blank=True)

    objects = TransferStripeManager()

    class Meta:
        app_label = 'ach'
        verbose_name = 'charge'
        verbose_name_plural = 'charges'
        ordering = ['created_at']

    def __str__(self):
        return self.stripe_id


@admin.register(TransferStripe)
class TransferStripeAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'stripe_id',
        'account',
        'status',
        'amount',
        'description',
        'failure_code',
        'failure_message',
        'paid',
        'is_processed_to_user',
        'processed_at'
    )
    readonly_fields = (
        'account',
        'stripe_id',
        'status',
        'amount',
        'amount_stripe',
        'balance_transaction',
        'currency',
        'captured',
        'description',
        'failure_code',
        'failure_message',
        'livemode',
        'metadata',
        'paid',
        'source',
        'created_at',
        'is_processed_to_user',
        'processed_at'
    )
