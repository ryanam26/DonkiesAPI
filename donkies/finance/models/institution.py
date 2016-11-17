import logging
from django.db import models
from django.contrib import admin
from django.db import transaction
from django.apps import apps
from finance.services.atrium_api import AtriumApi

logger = logging.getLogger('app')


class InstitutionManager(models.Manager):
    @transaction.atomic
    def update_credentials(self):
        """
        Updates all credentials of institutions
        that are marked as "is_update".

        TODO: processing errors from Atrium API.
        """
        Credentials = apps.get_model('finance', 'Credentials')

        for i in Institution.objects.filter(is_update=True):
            Credentials.objects.update_all_credentials(i.code)

    @transaction.atomic
    def update_list(self):
        """
        Updates all institutions.
        If find new institutions, add them to database.
        Updates existing institutions.

        TODO: process error response from Atrium API.
        """
        page = 1
        records_per_page = 100
        a = AtriumApi()

        while True:
            res = a.search_institutions(
                records_per_page=records_per_page, page=page)

            for d in res['institutions']:
                self.update(**d)

            if res['pagination']['total_pages'] >= page:
                break

            page += 1

    def update(self, code, name, url):
        try:
            i = Institution.objects.get(code=code)
            if i.name != name or i.url != url:
                i.name = name
                i.url = url
                i.save()
            return
        except Institution.DoesNotExist:
            i = Institution(code=code, name=name, url=url)
            i.save()
            logger.info('New institution found: {}'.format(code))


class Institution(models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    sort = models.IntegerField(default=0)
    is_update = models.BooleanField(
        default=True,
        help_text='Update credentials of the institution on scheduled task')
    last_update = models.DateTimeField(auto_now=True)

    objects = InstitutionManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'institution'
        verbose_name_plural = 'institutions'
        ordering = ['sort', 'name']

    def __str__(self):
        return self.code


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'name',
        'url',
        'sort',
        'is_update',
        'last_update'
    )
    list_editable = ('sort', 'is_update')
    search_fields = ('name', 'code')
