from django.db import models
from django.contrib import admin
from django.apps import apps
from bank.services.dwolla_api import DwollaApi


class TransferManager(models.Manager):
    """
    Transfer flow.
    1) Transfer is created in database.
    2) Periodic celery task processed all transfers.
    """
    def create_transfer(self, src_id, dst_id, amount):
        FundingSource = apps.get_model('bank', 'FundingSource')
        src = FundingSource.objects.get(src_id)
        dst = FundingSource.objects.get(dst_id)
        t = self.model(source=src, destination=dst, amount=amount)
        t.save()
        return t

    def create_dwolla_transfer(self, id):
        t = self.model.objects.get(id)
        if t.dwolla_id is not None:
            return

        dw = DwollaApi()
        id = dw.create_transfer(
            t.source.dwolla_id, t.destination.dwolla_id, str(t.amount))
        if id is not None:
            t.dwolla_id = id
            t.save()

    def update_transfer(self, id):
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


class Transfer(models.Model):
    PENDING = 'pending'
    PROCESSED = 'processed'
    CANCELLED = 'cancelled'
    FAILED = 'failed'
    RECLAIMED = 'reclaimed'

    STATUS_CHOICES = (
        (PENDING, 'pending'),
        (PROCESSED, 'processed'),
        (CANCELLED, 'cancelled'),
        (FAILED, 'failed'),
        (RECLAIMED, 'reclaimed')
    )

    dwolla_id = models.CharField(
        max_length=50, null=True, default=None, blank=True, unique=True)
    source = models.ForeignKey('FundingSource', related_name='source')
    destination = models.ForeignKey(
        'FundingSource', related_name='destination')
    status = models.CharField(
        max_length=9, null=True, default=None, choices=STATUS_CHOICES)
    failure_code = models.CharField(
        max_length=3, null=True, default=None, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    last_update = models.DateTimeField(null=True, default=None, blank=True)
    created_at = models.DateTimeField(null=True, default=None, blank=True)
    is_done = models.BooleanField(default=False)

    objects = TransferManager()

    class Meta:
        app_label = 'bank'
        verbose_name = 'transfer'
        verbose_name_plural = 'transfers'
        ordering = ['-created_at']

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        if self.status not in [None, self.PENDING]:
            self.is_done = True
        super().save(*args, **kwargs)


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = (
        'dwolla_id',
        'source',
        'destination',
        'status',
        'failure_code',
        'amount',
        'last_update',
        'created_at'
    )
