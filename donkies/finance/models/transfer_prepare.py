"""
Transfer flow.

First, we collect roundup to TransferPrepare.
Then from TransferPrepare total user's roundup amount
processed to:

1) If Dwolla implementation:

To TransferDonkies model (if user set funding source account).
From TransferDonkies model we send transfer to Donkies LLC (via Dwolla).

2) If Stripe implementation:

To TransferStripe model. (if user set funding source account).
In Stripe the first debit account is automatically funding source.
Money transferred to Stripe account that related to Plaid.

The money hold on Donkies account.
On 15th of current month all funds that collected for previous month
(if user set is_auto_transfer
and if total amount more than minimum_transfer_amount)
send to TransferUser model.

From TransferUser model send funds to TransferDebt to
different debt accounts accordingly to share.

From TransferDebt currently send cheques to users manually.
"""
from django.db import models
from django.contrib import admin
from django.apps import apps
from django.db import transaction
from django.conf import settings


class TransferPrepareManager(models.Manager):
    def process_roundups(self):
        """
        Roundup transfer rule - by amount.
        As soon as collected roundup is more than
        settings.TRANSFER_TO_DONKIES_MIN_AMOUNT, send
        transfer to Donkies LLC.

        Called by celery scheduled task.
        Processes all roundups for all users to TransferPrepare.

        1) If user didn't set funding source, do not process user.

        2) Calculates total roundup from user's accounts.
           If sum more than TRANSFER_TO_DONKIES_MIN_AMOUNT
           - process user.
        """
        Account = apps.get_model('finance', 'Account')
        User = apps.get_model('web', 'User')

        for user in User.objects.filter(is_closed_account=False):
            fs = user.get_funding_source_account()
            if not fs:
                continue

            sum = user.get_not_processed_roundup_sum()
            if sum >= settings.TRANSFER_TO_DONKIES_MIN_AMOUNT:
                qs = Account.objects.active().filter(
                    type_ds=Account.DEBIT, item__user=user)
                self.process_roundup(list(qs))

    @transaction.atomic
    def process_roundup(self, accounts):
        """
        Process all not processed transactions for
        user's accounts.
        "accounts" - accounts  list.
        """
        for account in accounts:
            total = 0
            for tr in account.transactions.filter(is_processed=False):
                if tr.roundup == 0:
                    tr.is_processed = True
                    tr.save()
                    continue

                total += tr.roundup
                tr.is_processed = True
                tr.save()

            if total > 0:
                tpe = self.model(account=account, roundup=total)
                tpe.save()


class TransferPrepare(models.Model):
    """
    All roundups that were collected from debit account saved to model.
    All transactions that provide roundup set to is_processed=True
    """
    account = models.ForeignKey(
        'Account',
        related_name='transfers_prepare',
        help_text='Debit account.')
    roundup = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, default=None, blank=True)
    is_processed = models.BooleanField(default=False)

    objects = TransferPrepareManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'transfer prepare'
        verbose_name_plural = 'transfers prepare'
        ordering = ['-created_at']

    def __str__(self):
        return str(self.id)


@admin.register(TransferPrepare)
class TransferPrepareAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'account',
        'roundup',
        'is_processed',
        'processed_at'
    )
    readonly_fields = (
        'created_at',
        'account',
        'roundup',
        'is_processed',
        'processed_at'
    )

    def has_delete_permission(self, request, obj=None):
        return False
