from django.db import models
from django.contrib import admin


class Credentials(models.Model):
    institution = models.ForeignKey('Institution')
    guid = models.CharField(max_length=100, unique=True)
    field_name = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
    type = models.CharField(max_length=100)

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
