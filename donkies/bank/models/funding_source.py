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
        if fs.dwolla_id is not None:
            return

        data = {
            'routingNumber': fs.routing_number,
            'accountNumber': fs.account_number,
            'type': fs.type,
            'name': fs.name
        }
        dw = DwollaApi()
        id = dw.create_funding_source(fs.customer.dwolla_id, data)
        if id is not None:
            fs.dwolla_id = id
            fs.save()

    def init_dwolla_funding_source(self, id):
        fs = self.model.objects.get(id=id)
        if fs.dwolla_id is not None and fs.created_at is None:
            dw = DwollaApi()
            d = dw.get_funding_source(fs.dwolla_id)
            fs.dwolla_id = d['id']
            fs.created_at = d['created']
            fs.status = d['status']
            fs.is_removed = d['removed']
            fs.typeb = d['type']
            fs.save()

    def init_micro_deposits(self, id):
        fs = self.model.objects.get(id=id)
        if fs.md_status is None:
            dw = DwollaApi()
            dw.init_micro_deposits(fs.dwolla_id)

    def update_micro_deposits(self, id):
        """
        Updates status of micro-deposits verification.
        """
        fs = self.model.objects.get(id=id)
        if fs.md_status is not None and fs.md_status != self.model.PROCESSED:
            dw = DwollaApi()
            d = dw.get_micro_deposits(fs.dwolla_id)
            fs.md_status = d['status']
            fs.md_created_at = d['created']
            fs.save()


class FundingSource(models.Model):
    VERIFIED = 'verified'
    UNVERIFIED = 'unverified'

    CHECKING = 'checking'
    SAVINGS = 'savings'

    BANK = 'bank'
    BALANCE = 'balance'

    MICRO_DEPOSIT = 'micro-deposit'
    IAV = 'iav'

    PENDING = 'pending'
    PROCESSED = 'processed'

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

    VERIFICATION_CHOICES = (
        (MICRO_DEPOSIT, 'micro deposit'),
        (IAV, 'instant verification')
    )

    account = models.OneToOneField('finance.Account')
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
    verification_type = models.CharField(
        max_length=20, choices=VERIFICATION_CHOICES, default=MICRO_DEPOSIT)
    md_status = models.CharField(
        max_length=20, null=True, default=None, blank=True,
        help_text='Micro-deposits verification status')
    md_created_at = models.DateTimeField(
        null=True, default=None, blank=True,
        help_text='Micro-deposits created time.')

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
        'is_removed',
        'verification_type',
        'md_status',
        'md_created_at'
    )
    list_filter = ('is_removed',)