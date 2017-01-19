from django.db import models
from django.contrib import admin
from finance.models import TransferDwolla
from bank.services.dwolla_api import DwollaApi


class TransferDonkiesFailedManager(models.Manager):
    def update_dwolla_failure_code(self, id):
        tdf = self.models.objects.get(id=id)
        if tdf.failure_code is not None:
            return

        dw = DwollaApi()
        code = dw.get_transfer_failure_code(tdf.dwolla_id)

        if code is not None:
            tdf.failure_code = code
            tdf.save()


class TransferDonkiesFailed(TransferDwolla):
    """
    Before initiate transfer, there is a check for
    sufficient amount for transfer.

    When transfer failed for other reason,
    it means something serious and very rare.
    (all other reasons will remove bank account from Dwolla.)

    Therefore move this rare info from TransferDonkies to TransferDonkiesFailed
    and process this cases manually.
    """
    account = models.ForeignKey(
        'Account',
        help_text='Funding source user debit account.')
    failure_code = models.CharField(
        max_length=4, null=True, default=None, blank=True)
    failed_at = models.DateTimeField(null=True, default=None, blank=True)

    objects = TransferDonkiesFailedManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'transfer donkies failed'
        verbose_name_plural = 'transfers donkies failed'
        ordering = ['-created_at']

    def __str__(self):
        return str(self.id)


@admin.register(TransferDonkiesFailed)
class TransferDonkiesAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'failed_at',
        'account',
        'amount',
        'status',
        'failure_code',
        'dwolla_id'
    )
    readonly_fields = (
        'created_at',
        'failed_at',
        'account',
        'amount',
        'status',
        'failure_code',
        'dwolla_id'
    )

    def has_delete_permission(self, request, obj=None):
        return False
