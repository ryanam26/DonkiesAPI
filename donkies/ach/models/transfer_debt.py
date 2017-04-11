from django.db import models
from django.contrib import admin


class TransferDebtManager(models.Manager):
    pass


class TransferDebt(models.Model):
    """
    After all data have been processed to TransferDebt model,
    send payment to user's debt accounts.
    In current implementations by cheques manually.
    """
    account = models.ForeignKey(
        'finance.Account',
        related_name='transfers_user',
        help_text='Debt account.')
    tu = models.ForeignKey(
        'TransferUser', help_text='TransferUser transfer')
    share = models.IntegerField(help_text='Current share on processing date.')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    processed_at = models.DateTimeField(null=True, default=None, blank=True)
    is_processed = models.BooleanField(default=False)

    objects = TransferDebtManager()

    class Meta:
        app_label = 'ach'
        verbose_name = 'transfer debt'
        verbose_name_plural = 'transfers debt'
        ordering = ['-processed_at']

    def __str__(self):
        return str(self.id)


@admin.register(TransferDebt)
class TransferDebtAdmin(admin.ModelAdmin):
    list_display = (
        'account',
        'tu',
        'share',
        'amount',
        'processed_at',
        'is_processed'
    )
