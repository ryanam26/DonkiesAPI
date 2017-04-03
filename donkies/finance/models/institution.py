from django.db import models
from django.contrib import admin
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

    def create_institution(self, name, plaid_id):
        try:
            i = self.model.objects.get(plaid_id=plaid_id)
        except self.model.DoesNotExist:
            i = self.model(name=name, plaid_id=plaid_id)
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
            self.create_institution(name, plaid_id)


class Institution(models.Model):
    plaid_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    has_mfa = models.BooleanField(default=False)
    mfa = JSONField(null=True, default=None)
    credentials = JSONField(null=True, default=None)
    products = JSONField(null=True, default=None)

    sort = models.IntegerField(default=0)

    objects = InstitutionManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'institution'
        verbose_name_plural = 'institutions'
        ordering = ['sort', 'name']

    def __str__(self):
        return self.name


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'plaid_id',
        'sort',
    )
    list_editable = ('sort',)
    search_fields = ('name', 'plaid_id')
    readonly_fields = (
        'plaid_id',
        'name'
    )
