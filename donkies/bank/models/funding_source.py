from django.db import models
from django.contrib import admin
from bank.services.dwolla_api import DwollaApi


class FundingSourceManager(models.Manager):
    def create_funding_source(
            self, account, account_number, routing_number, name, type):

        fs = self.model(
            account=account, account_number=account_number,
            routing_number=routing_number, name=name, type=type)
        fs.save()
        return fs

    def create_dwolla_funding_source(self, id):
        fs = self.model.objects.get(id=id)
        data = {
            'routingNumber': fs.routing_number,
            'accountNumber': fs.account_number,
            'type': fs.type,
            'name': fs.name
        }
        dw = DwollaApi()
        dw.create_funding_source(fs.customer.id, data)

    def init_dwolla_funding_source(self, id):
        fs = self.model.objects.get(id=id)
        dw = DwollaApi()
        d = dw.get_funding_source_by_name(fs.name)
        if d is not None:
            fs.dwolla_id = d['id']
            fs.created_at = d['created']
            fs.status = d['status']
            fs.is_removed = d['removed']
            fs.typeb = d['type']
            fs.save()


class FundingSource(models.Model):
    VERIFIED = 'verified'
    UNVERIFIED = 'unverified'

    CHECKING = 'checking'
    SAVINGS = 'savings'

    BANK = 'bank'
    BALANCE = 'balance'

    STATUS_CHOICES = (
        (VERIFIED, 'verified'),
        (UNVERIFIED, 'unverified')
    )

    TYPE_CHOICES = (
        (CHECKING, 'checking'),
        (SAVINGS, 'savings')
    )

    TYPEB_CHOICES = (
        (BANK, 'bank'),
        (BALANCE, 'balance')
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
    typeb = models.CharField(
        max_length=7, choices=TYPEB_CHOICES, null=True, default=None)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(null=True, default=None, blank=True)
    is_removed = models.BooleanField(default=False)

    objects = FundingSourceManager()

    class Meta:
        app_label = 'bank'
        verbose_name = 'funding source'
        verbose_name_plural = 'funding sources'
        ordering = ['-created_at']
        unique_together = ['account', 'name']

    def __str__(self):
        return self.name

    @property
    def customer(self):
        return self.account.member.user.customer


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
        'typeb',
        'created_at',
        'is_removed',
    )
    readonly_fields = (
        'account_number',
        'routing_number',
        'dwolla_id',
        'status',
        'type',
        'typeb',
        'created_at',
        'is_removed'
    )
    list_filter = ('is_removed',)
