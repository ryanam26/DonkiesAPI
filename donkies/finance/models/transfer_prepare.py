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
import calendar
import datetime
from django.db import models
from django.contrib import admin
from django.apps import apps
from django.db import transaction


class TransferPrepareManager(models.Manager):
    def process_roundups(self, is_test=False):
        """
        Called by celery scheduled task.
        Check if current date is date of transfer, process
        all roundups for all users to TransferPrepare.
        """
        Account = apps.get_model('finance', 'Account')

        dt = datetime.today() if is_test else self.get_transfer_date()
        if dt == datetime.today():
            for account in Account.objects.active():
                self.process_roundup(account)

    @transaction.atomic
    def process_roundup(self, account):
        """
        Process all not processed transactions for account.
        """
        for tr in account.transactions.filter(is_processed=False):
            if tr.roundup == 0:
                tr.is_processed = True
                tr.save()
                continue
            tpe = self.model(account=account, roundup=tr.roundup)
            tpe.save()

            tr.is_processed = True
            tr.save()

    def get_transfer_date(self, is_test=False):
        """
        Returns the date when all transfers should be made.
        The last day of the month.
        """
        today = datetime.date.today()
        _, last = calendar.monthrange(today.year, today.month)
        return last


class TransferPrepare(models.Model):
    """
    This model contains data for transfers by dates.
    All roundup that were collected from debit account saved to model.
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
