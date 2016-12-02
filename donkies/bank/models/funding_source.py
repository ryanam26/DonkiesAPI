from django.db import models
from django.contrib import admin


class FundingSourceManager(models.Manager):
    def create_funding_source(
            self, account, account_number, routing_number, name, type):

        fs = self.model(
            account=account, account_number=account_number,
            routing_number=routing_number, name=name, type=type)
        fs.save()
        return fs


class FundingSource(models.Model):
    VERIFIED = 'verified'
    UNVERIFIED = 'unverified'

    CHECKING = 'checking'
    SAVINGS = 'savings'

    STATUS_CHOICES = (
        (VERIFIED, 'verified'),
        (UNVERIFIED, 'unverified')
    )

    TYPE_CHOICES = (
        (CHECKING, 'checking'),
        (SAVINGS, 'savings')
    )

    account = models.ForeignKey('finance.Account')
    dwolla_id = models.CharField(
        max_length=50, null=True, default=None, blank=True, unique=True)
    account_number = models.CharField(max_length=100)
    routing_number = models.CharField(max_length=100)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=UNVERIFIED)
    type = models.CharField(max_length=8, choices=TYPE_CHOICES)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(null=True, default=None, blank=True)
    is_removed = models.BooleanField(default=False)

    objects = FundingSourceManager()

    class Meta:
        app_label = 'bank'
        verbose_name = 'funding source'
        verbose_name_plural = 'funding sources'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


@admin.register(FundingSource)
class FundingSourceAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'account',
        'account_number',
        'routing_number',
        'dwolla_id',
        'status',
        'type',
        'created_at',
        'is_removed',
    )
    list_filter = ('is_removed',)
