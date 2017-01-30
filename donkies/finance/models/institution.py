import logging
import time
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

        fields = ['name', 'code', 'url', 'small_logo_url', 'medium_logo_url']

        while True:
            time.sleep(1)
            res = a.search_institutions(
                records_per_page=records_per_page, page=page)

            for d in res['institutions']:
                for k in d:
                    if k not in fields:
                        d.pop(k)
                self.update(**d)

            if res['pagination']['total_pages'] <= page:
                break

            page += 1

    def update(
            self, code, name, url, small_logo_url=None, medium_logo_url=None):

        if not code:
            return

        try:
            logger.info('{} {}'.format(name, small_logo_url))
            i = Institution.objects.get(code=code)
            is_update = False
            for field in ['name', 'url', 'small_logo_url', 'medium_logo_url']:
                if getattr(i, field) != locals()[field]:
                    is_update = True

            if is_update:
                i.name = name
                i.url = url
                i.small_logo_url = small_logo_url
                i.medium_logo_url = medium_logo_url
                i.save()
            return
        except Institution.DoesNotExist:
            i = Institution(
                code=code,
                name=name,
                url=url,
                small_logo_url=small_logo_url,
                medium_logo_url=medium_logo_url
            )
            i.save()
            logger.info('New institution found: {}'.format(code))


class Institution(models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    small_logo_url = models.CharField(
        max_length=255, null=True, default=None, blank=True)
    medium_logo_url = models.CharField(
        max_length=255, null=True, default=None, blank=True)
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
    readonly_fields = (
        'code',
        'name',
        'url',
        'small_logo_url',
        'medium_logo_url'
    )
