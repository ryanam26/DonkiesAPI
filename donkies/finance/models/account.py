from django.db import models
from django.contrib import admin


class Account(models.Model):
    member = models.ForeignKey('Member')
    guid = models.CharField(max_length=100, unique=True)
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
    is_closed = models.ForeignKey(default=False)
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
    updated_at = models.DateTimeField(null=True, default=None)

    class Meta:
        app_label = 'finance'
        verbose_name = 'account'
        verbose_name_plural = 'accounts'
        ordering = ['member']

    def __str__(self):
        if self.name:
            return self.name
        return self.guid


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    pass
