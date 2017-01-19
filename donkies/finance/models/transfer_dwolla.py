from django.db import models


class TransferDwolla(models.Model):
    """
    Abstract model for TransferDonkies and TransferDonkiesFailed.
    """

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
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=9, null=True, default=None, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(null=True, default=None, blank=True)
    initiated_at = models.DateTimeField(null=True, default=None, blank=True)
    updated_at = models.DateTimeField(null=True, default=None, blank=True)
    failure_code = models.CharField(
        max_length=4, null=True, default=None, blank=True)
    is_initiated = models.BooleanField(
        default=False, help_text='Transfer initiated in Dwolla')
    is_failed = models.BooleanField(default=False)

    class Meta:
        abstract = True
