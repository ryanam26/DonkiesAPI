"""
Customers in model created by periodic celery task.
Customer can be created as soon as user completed profile.

Also customers can be created by API. There is API endpoint.

Customers created in Dwolla by periodic celery task.
"""


import datetime
from django.db import models
from django.contrib import admin
from web.services.helpers import to_camel
from bank.services.dwolla_api import DwollaApi


class CustomerManager(models.Manager):
    def create_customer(self, user, type=None):
        if type is None:
            type = self.model.PERSONAL

        c = self.model(user=user, type=type)
        c.save()
        return c

    def create_dwolla_customer(self, id):
        """
        Celery task POST call to dwolla to create customer.
        """
        customer = self.model.objects.get(id=id)
        if customer.dwolla_id is not None:
            return

        dic = self.get_customer_data_for_create_request(customer)

        dw = DwollaApi()
        id = dw.create_customer(dic)
        if id is not None:
            customer.dwolla_id = id
            customer.save()

    def get_customer_data_for_create_request(self, customer):
        """
        Returns dict with data to create customer in Dwolla.
        """
        fields = [
            'first_name', 'last_name', 'email', 'type', 'address1',
            'city', 'state', 'postal_code', 'date_of_birth', 'ssn',
            'ip_address', 'address2', 'phone']

        d = {}
        for field in fields:
            value = getattr(customer, field)
            if value:
                if isinstance(value, datetime.date):
                    value = value.strftime('%Y-%m-%d')
                d[to_camel(field)] = value
        return d

    def initiate_dwolla_customer(self, id):
        """
        Get data of created, but not initiated yet customer.
        """
        c = self.model.objects.get(id=id)
        if c.dwolla_id is not None and c.created_at is None:
            dw = DwollaApi()
            d = dw.get_customer(c.dwolla_id)
            if d is not None:
                assert d['id'] == c.dwolla_id
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

    user = models.OneToOneField('web.User', related_name='customer')
    ip_address = models.CharField(
        max_length=50, null=True, default=None, blank=True)
    type = models.CharField(
        max_length=10, choices=TYPE_CHOICES, default=PERSONAL)
    dwolla_type = models.CharField(
        max_length=10, choices=DWOLLA_TYPE_CHOICES, default=UNVERIFIED)
    dwolla_id = models.CharField(
        max_length=50, null=True, default=None, blank=True, unique=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=UNVERIFIED)
    created_at = models.DateTimeField(
        null=True, default=None, blank=True, help_text='Created at dwolla.')

    objects = CustomerManager()

    class Meta:
        app_label = 'bank'
        verbose_name = 'customer'
        verbose_name_plural = 'customers'
        ordering = ['-created_at']

    def __str__(self):
        return self.user.email

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def email(self):
        return self.user.email

    @property
    def address1(self):
        return self.user.address1

    @property
    def address2(self):
        return self.user.address2

    @property
    def city(self):
        return self.user.city

    @property
    def state(self):
        return self.user.state

    @property
    def postal_code(self):
        return self.user.postal_code

    @property
    def date_of_birth(self):
        return self.user.date_of_birth

    @property
    def ssn(self):
        return self.user.ssn

    @property
    def phone(self):
        return self.user.phone


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
    readonly_fields = (
        'dwolla_id',
        'status',
        'created_at'
    )
