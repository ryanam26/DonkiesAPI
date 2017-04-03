from django.db import models
from django.contrib import admin


class InstitutionManager(models.Manager):
    def get_or_create_institution(self, name, plaid_id):
        try:
            i = self.model.objects.get(plaid_id=plaid_id)
        except self.model.DoesNotExist:
            i = self.model(name=name, plaid_id=plaid_id)
            i.save()
        return i


class Institution(models.Model):
    plaid_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    url = models.CharField(
        max_length=255, null=True, default=None, blank=True)
    small_logo_url = models.CharField(
        max_length=255, null=True, default=None, blank=True)
    medium_logo_url = models.CharField(
        max_length=255, null=True, default=None, blank=True)
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
        'url',
        'sort',
    )
    list_editable = ('sort',)
    search_fields = ('name', 'plaid_id')
    readonly_fields = (
        'plaid_id',
        'name',
        'url',
    )
