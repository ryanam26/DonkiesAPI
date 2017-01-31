"""
Transfer flow.

First we collect roundup to TransferPrepare.
Then from TransferPrepare total user's roundup amount
processed to TransferDonkies model (if user set funding source account).
From TransferDonkies model we send transfer to Donkies LLC (via Dwolla).
As soon as money received by Donkies LLC, we process received amount to
debt user's accounts to TransferUser model.

From TransferUser model currently send cheques manually.
"""
from django.db import models
from django.contrib import admin
from django.apps import apps
from django.db import transaction


class TransferPrepareManager(models.Manager):
    def process_roundups(self):
        """
        Called by celery scheduled task.
        Processes all roundups for all users to TransferPrepare.

        1) If user didn't set funding source, do not process user.

        2) Calculates total roundup from user's accounts.
           If sum less than user set in minimum_transfer_amount,
           do not process user.
        """
        Account = apps.get_model('finance', 'Account')
        User = apps.get_model('web', 'User')
        for user in User.objects.all():
            fs = user.get_funding_source_account()
            if not fs:
                continue

            sum = user.get_not_processed_roundup_sum()
            if sum >= user.minimum_transfer_amount:
                qs = Account.objects.active().filter(
                    type_ds=Account.DEBIT, member__user=user)

                for account in qs:
                    self.process_roundup(account)

    @transaction.atomic
    def process_roundup(self, account):
        """
        Process all not processed transactions for account.
        """
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
    This model contains data for transfers by dates.
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
