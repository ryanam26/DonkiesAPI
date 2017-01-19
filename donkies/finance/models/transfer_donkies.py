"""
Info about Dwolla transfers and failure codes:
https://developers.dwolla.com/resources/bank-transfer-workflow/transfer-failures.html

Transfer flow from TransferDonkies to Donkies LLC on Dwolla.

1) Celery scheduled task "initiate_dwolla_transfers" look at all transfers
   that is_initiated = False and run manager's method
   "initiate_dwolla_transfer" for each transfer.

   When get success respond from Dwolla, set
    is_initiated = True
    intiated_at = now
    updated_at = now
    dwolla_id = received dwolla id

2) Celery scheduled task "update_dwolla_transfers" look at all transfers
   that is_initiated = True, is_sent = False, is_failed=False
   and run manager's method
   "update_dwolla_transfer" for each transfer.

   If less than 15 minutes from last check, do nothing.

   Send request to Dwolla to get status of transfer.

   1) If status == pending, set:
      updated_at = now

   2) If status == processed, set:
      is_sent = True
      sent_at = the date of transfer
      updated_at = now

   3) If other status, set:
      updated_at = now
      is_failed = True

3) Celery scheduled task "update_dwolla_failure_codes" look at all transfers
   that is_failed = True and failure_code = None and run
   manager's method "update_dwolla_failure_code".

   Send request to Dwolla and set:

   failure_code = code
   updated_at = now

   If failure_code == R01, it means "Insufficient funds", other task will
   reinitiate this transfer after 24 hours.

   Else: something bad happened, move all data from TransferDonkies to
   TransferDonkiesFailed for manual processing.

4) Celery scheduled task "reinitiate_dwolla_transfers" look at all transfers
   that failure_code = R01 and today date > updated_at + 24 hours. Set:

   is_initiated = False
   is_failed = False
   failure_code = None
"""

import datetime
from django.db import models
from django.contrib import admin
from django.apps import apps
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from bank.services.dwolla_api import DwollaApi
from finance.models import TransferDwolla


class TransferDonkiesManager(models.Manager):
    def process_prepare(self):
        """
        Called by celery scheduled task.
        Process TransferPrepare to TransferDonkies model.
        """
        TransferPrepare = apps.get_model('finance', 'TransferPrepare')

        users = TransferPrepare.objects.filter(is_processed=False)\
            .order_by('account__member__user_id')\
            .values_list('account__member__user_id', flat=True)\
            .distinct()

        for user_id in users:
            self.process_prepare_user(user_id)

    @transaction.atomic
    def process_prepare_user(self, user_id):
        """
        If user has not set funding source yet, do not move
        funds from TransferPrepare to TransferDonkies.
        """
        TransferPrepare = apps.get_model('finance', 'TransferPrepare')
        User = apps.get_model('web', 'User')

        user = User.objects.get(id=user_id)
        fs = user.get_funding_source_account()
        if fs is None:
            return

        sum = TransferPrepare.objects.filter(
            is_processed=False,
            account__member__user=user)\
            .aggregate(Sum('roundup'))['roundup__sum']

        TransferPrepare.objects.filter(
            is_processed=False,
            account__member__user=user).update(is_processed=True)

        tds = self.model(account=fs, amount=sum)
        tds.save()

    def initiate_dwolla_transfer(self, id):
        tds = self.model.objects.get(id)
        if not tds.can_initiate:
            return

        fs = tds.account.funding_source

        dw = DwollaApi()
        id = dw.initiate_transfer(fs.dwolla_id, str(tds.amount))
        if id is not None:
            tds.dwolla_id = id
            tds.is_initiated = True
            tds.intiated_at = timezone.now()
            tds.updated_at = timezone.now()
            tds.save()

    def update_dwolla_transfer(self, id, is_test=False):
        """
        If less than 15 minutes from last check, do nothing.
        """
        tds = self.model.objects.get(id)
        if not tds.can_update:
            return

        now = timezone.now()
        if tds.updated_at + datetime.timedelta(minutes=15) > now:
            if not is_test:
                return

        dw = DwollaApi()
        d = dw.get_transfer(tds.dwolla_id)
        if d['status'] == self.model.FAILED:
            dw.get_transfer_failure(tds.dwolla_id)
            tds.status = d['status']
            tds.failure_code = dw.get_transfer_failure(tds.dwolla_id)
            tds.save()
            return

        if tds.status != d['status']:
            tds.status = d['status']
            tds.save()

    def update_dwolla_failure_code(self, id):
        tds = self.models.objects.get(id=id)
        if tds.failure_code is not None:
            return

        dw = DwollaApi()
        code = dw.get_transfer_failure_code(tds.dwolla_id)

        if code is not None:
            tds.failure_code = code
            tds.updated_at = timezone.now()
            tds.save()


class TransferDonkies(TransferDwolla):
    """
    If user set funding source debit account, transfer all
    amount for particular user from TransferPrepare to this model.
    Then send money to Donkeys LLC (via Dwolla)

    As soon as money has been sent to Donkeys - set is_sent = True
    Check by API receiving money to Donkeys LLC account and as
    soon as money received - set is_received = True

    Process received amount to user debt's accounts accordingly to share
    to TransferUser model.
    """
    account = models.ForeignKey(
        'Account',
        related_name='transfers_donkies',
        help_text='Funding source user debit account.')
    sent_at = models.DateTimeField(null=True, default=None, blank=True)
    processed_at = models.DateTimeField(null=True, default=None, blank=True)
    is_sent = models.BooleanField(
        default=False, help_text='Money sent to Donkies LLC')
    is_processed_to_user = models.BooleanField(
        default=False, help_text='Funds processed to TransferUser model.')

    objects = TransferDonkiesManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'transfer donkies'
        verbose_name_plural = 'transfers donkies'
        ordering = ['-created_at']

    def __str__(self):
        return str(self.id)

    @property
    def can_initiate(self):
        if self.is_initiated:
            return False
        return True

    @property
    def can_update(self):
        if self.is_sent or self.is_failed or not self.is_initiated:
            return False
        if not self.dwolla_id:
            return False
        return True


@admin.register(TransferDonkies)
class TransferDonkiesAdmin(admin.ModelAdmin):
    list_display = (
        'account',
        'amount',
        'created_at',
        'sent_at',
        'processed_at',
        'is_initiated',
        'is_sent',
        'is_processed_to_user'
    )
    readonly_fields = (
        'dwolla_id',
        'account',
        'amount',
        'created_at',
        'initiated_at',
        'sent_at',
        'processed_at',
        'is_initiated',
        'is_sent',
        'is_processed_to_user'
    )

    def has_delete_permission(self, request, obj=None):
        return False
