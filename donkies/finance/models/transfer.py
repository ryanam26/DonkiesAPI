from django.db import models
from django.contrib import admin
from django.utils import timezone


class TransferManager(models.Manager):
    def create_transfer(self, account_from, account_to, transaction):
        t = self.model(
            account_from=account_from,
            account_to=account_to,
            transaction=transaction)
        t.save()
        return t


class Transfer(models.Model):
    account_from = models.ForeignKey('Account', related_name='transfers_from')
    account_to = models.ForeignKey('Account', related_name='transfers_to')
    transaction = models.ForeignKey('Transaction')
    dt = models.DateTimeField(default=timezone.now)
    is_processed = models.BooleanField(default=False)

    objects = TransferManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'transfer'
        verbose_name_plural = 'transfers'
        ordering = ['dt']

    def __str__(self):
        return str(self.id)


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = (
        'dt',
        'account_from',
        'account_to',
        'transaction',
        'is_processed'
    )
