from django.db import models
from django.contrib import admin
from django import forms
from django.db import transaction
from django.contrib.postgres.fields import JSONField
from finance.services.plaid_api import PlaidApi


class InstitutionManager(models.Manager):
    def get_or_create_institution(self, plaid_id):
        """
        If institution does not exist in database,
        query it from plaid API and save to db.
        """
        try:
            i = self.model.objects.get(plaid_id=plaid_id)
        except self.model.DoesNotExist:
            pa = PlaidApi()
            d = pa.get_institution(plaid_id)
            i = self.model(
                plaid_id=d['institution_id'],
                name=d['name'],
                products=d.get('products', None),
                credentials=d.get('credentials', None),
                has_mfa=d.get('has_mfa', None)
            )
            i.save()
        return i

    def create_institution(self, api_data):
        """
        Creates or updates.
        """
        d = api_data
        try:
            i = self.model.objects.get(plaid_id=d['institution_id'])
        except self.model.DoesNotExist:
            i = self.model(plaid_id=d['institution_id'])

        i.name = d['name']
        i.products = d.get('products', None)
        i.credentials = d.get('credentials', None)
        i.has_mfa = d.get('has_mfa', None)
        i.mfa = d.get('mfa', None)
        i.save()
        return i

    def create_sandbox_institutions(self):
        """
        Used for sandbox tests.
        """
        l = [
            ('First Platypus Bank', 'ins_109508'),
            ('First Gingham Credit Union', 'ins_109509'),
            ('Tattersall Federal Credit Union', 'ins_109510'),
            ('Tartan Bank', 'ins_109511'),
            ('Houndstooth Bank', 'ins_109512')
        ]
        for name, plaid_id in l:
            self.create_sandbox_institution(name, plaid_id)

    def create_sandbox_institution(self, name, plaid_id):
        try:
            i = self.model.objects.get(plaid_id=plaid_id)
        except self.model.DoesNotExist:
            i = self.model(name=name, plaid_id=plaid_id)
            i.save()
        return i

    @transaction.atomic
    def fetch_all_institutions(self):
        """
        Fetch all institutions from Plaid and save to db.
        """
        pa = PlaidApi()
        d = pa.get_institutions(100, offset=0)
        institutions = d['institutions']
        for data in institutions:
            self.create_institution(data)

        while len(institutions) < d['total']:
            d = pa.get_institutions(100, offset=len(institutions))
            for data in d['institutions']:
                self.create_institution(data)
            institutions.extend(d['institutions'])
            print(len(institutions))


class Institution(models.Model):
    plaid_id = models.CharField(
        max_length=100, unique=True, null=True, default=None,
        help_text='None for manual institutions.')
    name = models.CharField(max_length=255)
    has_mfa = models.BooleanField(default=False)
    mfa = JSONField(null=True, default=None)
    credentials = JSONField(null=True, default=None)
    products = JSONField(null=True, default=None)
    address = models.CharField(
        max_length=500, null=True, default=None, blank=True,
        help_text='Used for manual institutions.')
    is_manual = models.BooleanField(
        default=False,
        help_text='Used for debt accounts. Not exist in Plaid.')

    sort = models.IntegerField(default=0)

    objects = InstitutionManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'institution'
        verbose_name_plural = 'institutions'
        ordering = ['sort', 'name']

    def __str__(self):
        return self.name


class InstitutionAdminForm(forms.ModelForm):
    class Meta:
        model = Institution
        widgets = {
            'address': forms.Textarea(
                attrs={'cols': 50, 'rows': 10}),
        }
        fields = '__all__'


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    form = InstitutionAdminForm
    list_display = (
        'name',
        'address',
        'plaid_id',
        'has_mfa',
        'products',
        'sort',
        'is_manual'
    )
    list_filter = ('is_manual',)
    list_editable = ('sort',)
    search_fields = ('name', 'plaid_id', 'products')
    readonly_fields = (
        'plaid_id',
        'has_mfa',
        'mfa',
        'credentials',
        'products'
    )
