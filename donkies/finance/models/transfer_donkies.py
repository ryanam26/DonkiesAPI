"""
Info about transfers and failure codes:
https://developers.dwolla.com/resources/bank-transfer-workflow/transfer-failures.html

Transfer flow from TransferDonkies to Donkies LLC on Dwolla.

1) Celery scheduled task "initiate_dwolla_transfers" look at all transfers
   that is_initiated = False and runs manager's method
   "initiate_dwolla_transfer" for all transfers.

   Before initiate transfer in Dwolla, look if balance of source account
   has sufficient amount.

   When get success respond from Dwolla, set
    is_initiated = True
    intiated_at = now()
    dwolla_id = received dwollaid

2) 


"""


from django.db import models
from django.contrib import admin
from django.apps import apps
from django.db import transaction
from django.db.models import Sum
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
        t = self.model.objects.get(id)
        if t.dwolla_id is not None:
            return

        dw = DwollaApi()
        id = dw.create_transfer(
            t.source.dwolla_id, t.destination.dwolla_id, str(t.amount))
        if id is not None:
            t.dwolla_id = id
            t.save()

    def update_dwolla_transfer(self, id):
        """
        TODO: update created_at, when know total format of data.
        """
        t = self.model.objects.get(id)
        if t.is_done:
            return

        dw = DwollaApi()
        d = dw.get_transfer(t.dwolla_id)
        if d['status'] == self.model.FAILED:
            dw.get_transfer_failure(t.dwolla_id)
            t.status = d['status']
            t.failure_code = dw.get_transfer_failure(t.dwolla_id)
            t.save()
            return

        if t.status != d['status']:
            t.status = d['status']
            t.save()


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
    initiated_at = models.DateTimeField(null=True, default=None, blank=True)
    updated_at = models.DateTimeField(null=True, default=None, blank=True)
    sent_at = models.DateTimeField(null=True, default=None, blank=True)
    received_at = models.DateTimeField(null=True, default=None, blank=True)
    processed_at = models.DateTimeField(null=True, default=None, blank=True)
    is_initiated = models.BooleanField(
        default=False, help_text='Transfer initiated in Dwolla')
    is_sent = models.BooleanField(
        default=False, help_text='Money sent to Donkies LLC')
    is_received = models.BooleanField(
        default=False, help_text='Money received by Donkies LLC')
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


@admin.register(TransferDonkies)
class TransferDonkiesAdmin(admin.ModelAdmin):
    list_display = (
        'account',
        'amount',
        'created_at',
        'sent_at',
        'received_at',
        'processed_at',
        'is_initiated',
        'is_sent',
        'is_received',
        'is_processed_to_user'
    )
    readonly_fields = (
        'dwolla_id',
        'account',
        'amount',
        'created_at',
        'initiated_at',
        'sent_at',
        'received_at',
        'processed_at',
        'is_initiated',
        'is_sent',
        'is_received',
        'is_processed_to_user'
    )

    def has_delete_permission(self, request, obj=None):
        return False
