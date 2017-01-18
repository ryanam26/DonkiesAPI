from django.db import models
from django.contrib import admin


class TransferUserManager(models.Manager):
    pass


class TransferUser(models.Model):
    """
    As soon as Donkies LLC received money from user to bank account,
    process all data from TransferDonkies to TransferUser.
    Received amount should be splitted between all user's Debt accounts
    accordingly to share.

    After all data have been processed to TransferUser, send payment to user's
    debt accounts.

    In current implementations by cheques manually.
    """
    account = models.ForeignKey(
        'Account',
        related_name='transfers_user',
        help_text='Debt account.')
    td = models.ForeignKey(
        'TransferDonkies', help_text='Related TransferDonkies amount')
    share = models.IntegerField(help_text='Current share on processing date.')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, default=None, blank=True)
    is_processed = models.BooleanField(default=False)

    objects = TransferUserManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'transfer user'
        verbose_name_plural = 'transfers user'
        ordering = ['-created_at']

    def __str__(self):
        return str(self.id)


@admin.register(TransferUser)
class TransferUserAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'account',
        'td',
        'share',
        'amount',
        'processed_at',
        'is_processed'
    )
