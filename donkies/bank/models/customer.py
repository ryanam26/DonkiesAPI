import datetime
from django.db import models
from django.contrib import admin
from django.core.validators import RegexValidator
from web.services.helpers import to_camel
from bank.services.dwolla_api import DwollaApi


class CustomerManager(models.Manager):
    def create_customer(
            self, user, address1, city, state, postal_code,
            date_of_birth, ssn, type=None, address2=None, phone=None):
        """
        Customer is created by API from frontend.
        Then periodic celery task will create customer in Dwolla.
        """
        if type is None:
            type = self.model.PERSONAL

        c = self.model(
            user=user, address1=address1, city=city, state=state,
            postal_code=postal_code, date_of_birth=date_of_birth,
            ssn=ssn, type=type, address2=address2, phone=phone)
        c.save()
        return c

    def create_dwolla_customer(self, id):
        """
        1) Celery task POST call to dwolla to create customer.
        2) Should get 201. (Body is empty)
        3) Set is_created=True
        4) Other Celery task will fetch other info later.
        """
        c = self.model.objects.get(id=id)
        if c.is_created:
            return
        fields = [
            'first_name', 'last_name', 'email', 'type', 'address1',
            'city', 'state', 'postal_code', 'date_of_birth', 'ssn',
            'ip_address', 'address2', 'phone']

        d = {}
        for field in fields:
            value = getattr(c, field)
            if value is not None:
                if isinstance(value, datetime.date):
                    value = value.strftime('%Y-%m-%d')
                d[to_camel(field)] = value

        dw = DwollaApi()
        result = dw.create_customer(d)
        if result:
            c.is_created = True
            c.save()

    def init_dwolla_customer(self, id):
        """
        Get data of created, but not inited yet customer.
        """
        c = self.model.objects.get(id=id)
        if c.dwolla_id is not None:
            return

        dw = DwollaApi()
        d = dw.get_customer_by_email(c.email)
        if d is not None:
            c.dwolla_id = d['id']
            c.dwolla_type = d['type']
            c.status = d['status']
            c.created_at = d['created']
            c.save()


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
        max_length=11,
        validators=[
            RegexValidator(
                regex='^\d{3}\-\d{2}\-\d{4}$',
                message='Should be XXX-XX-XXXX')]
    )
    phone = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex='^\d{10}$',
                message='Should be 10 digits')],
        null=True,
        default=None,
        blank=True
    )
    dwolla_id = models.CharField(
        max_length=50, null=True, default=None, blank=True, unique=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=UNVERIFIED)
    created_at = models.DateTimeField(null=True, default=None, blank=True)
    is_created = models.BooleanField(
        default=False, help_text='Created in dwolla')

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
