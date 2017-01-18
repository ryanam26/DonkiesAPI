from django.db import models
from django.contrib import admin
from django.utils import timezone


class TransferUserManager(models.Manager):
    def create_transfer(self, account_from, account_to, transaction):
        t = self.model(
            account_from=account_from,
            account_to=account_to,
            transaction=transaction)
        t.save()
        return t


class TransferUser(models.Model):
    account_from = models.ForeignKey('Account', related_name='transfers_from')
    account_to = models.ForeignKey('Account', related_name='transfers_to')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    dt = models.DateTimeField(default=timezone.now)
    is_processed = models.BooleanField(default=False)

    objects = TransferUserManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'transfer'
        verbose_name_plural = 'transfers'
        ordering = ['-dt']

    def __str__(self):
        return str(self.id)


@admin.register(TransferUser)
class TransferUserAdmin(admin.ModelAdmin):
    list_display = (
        'dt',
        'account_from',
        'account_to',
        'amount',
        'is_processed'
    )
