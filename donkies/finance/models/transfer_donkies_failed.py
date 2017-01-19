from django.db import models
from django.contrib import admin
from finance.models import TransferDwolla


class TransferDonkiesFailed(TransferDwolla):
    """
    When transfer failure_code != R01
    it means something bad happened.
    (Most likely bank account removed from Dwolla.)

    Therefore move this items from TransferDonkies to TransferDonkiesFailed
    and process this cases manually.
    """
    account = models.ForeignKey(
        'Account',
        help_text='Funding source user debit account.')

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
        'updated_at',
        'account',
        'amount',
        'status',
        'failure_code',
        'dwolla_id'
    )
    readonly_fields = (
        'created_at',
        'updated_at',
        'account',
        'amount',
        'status',
        'failure_code',
        'dwolla_id'
    )

    def has_delete_permission(self, request, obj=None):
        return False
