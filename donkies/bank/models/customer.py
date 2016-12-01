from django.db import models
from django.contrib import admin
from django.core.validators import RegexValidator


class CustomerManager(models.Manager):
    pass


class Customer(models.Model):
    """
    Dwolla customer.
    If business type will be used - it requres additional fields.
    """
    PERSONAL = 'personal'
    BUSINESS = 'business'
    VERIFIED = 'verified'
    UNVERIFIED = 'unverified'

    TYPE_CHOICES = (
        (PERSONAL, 'personal'),
        (BUSINESS, 'business')
    )

    DWOLLA_TYPE_CHOICES = (
        (PERSONAL, 'personal'),
        (BUSINESS, 'business'),
        (UNVERIFIED, 'unverified')
    )

    STATUS_CHOICES = (
        (VERIFIED, 'verified'),
        (UNVERIFIED, 'unverified')
    )

    user = models.OneToOneField('web.User')
    ip_address = models.CharField(
        max_length=50, null=True, default=None, blank=True)
    type = models.CharField(
        max_length=10, choices=TYPE_CHOICES, default=PERSONAL)
    dwolla_type = models.CharField(
        max_length=10, choices=DWOLLA_TYPE_CHOICES, default=UNVERIFIED)
    address1 = models.CharField(max_length=50)
    address2 = models.CharField(
        max_length=50, null=True, default=None, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    postal_code = models.CharField(
        max_length=5,
        validators=[
            RegexValidator(
                regex='^\d{5}$',
                message='Should be 5 digits')]
    )
    date_of_birth = models.DateField(help_text='YYYY-MM-DD')
    ssn = models.CharField(
        help_text='Last 4 digits',
        max_length=4,
        validators=[
            RegexValidator(
                regex='^\d{4}$',
                message='Should be 4 digits')]
    )
    phone = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex='^\d{10}$',
                message='Should be 10 digits')]
    )
    dwolla_id = models.CharField(
        max_length=50, null=True, default=None, blank=True, unique=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=UNVERIFIED)
    created_at = models.DateTimeField(null=True, default=None, blank=True)

    objects = CustomerManager()

    class Meta:
        app_label = 'bank'
        verbose_name = 'customer'
        verbose_name_plural = 'customers'
        ordering = ['created_at']

    def __str__(self):
        return self.email

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def email(self):
        return self.user.email


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'first_name',
        'last_name',
        'type',
        'dwolla_type',
        'dwolla_id',
        'status',
        'city',
        'state',
        'postal_code',
        'date_of_birth',
        'ssn',
        'phone',
        'created_at'
    )
