from django.db import models
from django.contrib import admin
from django.apps import apps
from finance.services.atrium_api import AtriumApi


class CredentialManager(models.Manager):
    def update_all_credentials(self, code):
        """
        TODO: processing errors.
        """
        a = AtriumApi()
        l = a.get_credentials(code)
        for d in l:
            d['code'] = code
            self.create_or_update(**d)

    def create_or_update(
            self, code, guid, field_name, type, label):
        Institution = apps.get_model('finance', 'Institution')

        try:
            c = self.model.objects.get(guid=guid)
        except self.model.DoesNotExist:
            i = Institution.objects.get(code=code)
            c = self.model(institution=i, guid=guid)

        c.field_name = field_name
        c.type = type
        c.label = label
        c.save()
        return c

    def get_credential_guids(self, code):
        """
        Returns list of guids.
        """
        qs = self.model.objects.filter(institution__code=code)
        return [c.guid for c in qs]


class Credentials(models.Model):
    institution = models.ForeignKey('Institution')
    guid = models.CharField(max_length=100, unique=True)
    field_name = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
    type = models.CharField(max_length=100)

    objects = CredentialManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'credentials'
        verbose_name_plural = 'credentials'
        ordering = ['institution']

    def __str__(self):
        return '{}:{}'.format(self.institution.code, self.field_name)


@admin.register(Credentials)
class CredentialsAdmin(admin.ModelAdmin):
    list_display = (
        'guid',
        'institution',
        'field_name',
        'label',
        'type'
    )
