import datetime
from django.utils import timezone
from django.db import models
from django.contrib import admin
from django.contrib.postgres.fields import JSONField


class ChargeManager(models.Manager):
    def create_charge(self, account, stripe_charge):
        """
        stripe_charge - Stripe's API charge dict like object.
        """
        d = stripe_charge
        charge = self.model(account=account)

        dt = datetime.datetime.fromtimestamp(d.pop('created'))
        charge.created_at = timezone.make_aware(dt)
        charge.stripe_id = d.pop('id')

        fields = (
            'status', 'amount', 'balance_transaction', 'currency',
            'captured', 'description', 'failure_code', 'livemode',
            'metadata', 'paid', 'source')

        for key in fields:
            setattr(charge, key, d[key])

        charge.save()
        return charge


class Charge(models.Model):
    PENDING = 'pending'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'

    STATUS_CHOICES = (
        (PENDING, PENDING),
        (SUCCEEDED, SUCCEEDED),
        (FAILED, FAILED),
    )

    account = models.ForeignKey('finance.Account', related_name='charges')
    stripe_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(
        max_length=9, default=PENDING, choices=STATUS_CHOICES)
    amount = models.IntegerField(help_text='Amount in cents.')
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

    objects = ChargeManager()

    class Meta:
        app_label = 'ach'
        verbose_name = 'charge'
        verbose_name_plural = 'charges'
        ordering = ['created_at']

    def __str__(self):
        return self.stripe_id


@admin.register(Charge)
class ChargeAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'stripe_id',
        'account',
        'status',
        'amount',
        'description',
        'failure_code',
        'failure_message',
        'paid'
    )
    readonly_fields = (
        'account',
        'stripe_id',
        'status',
        'amount',
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
        'created_at'
    )
