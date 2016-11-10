from django.db import models
from django.contrib import admin


class Setting(models.Model):
    TYPES = [(1, 'str'), (2, 'int')]

    code = models.CharField(max_length=50)
    value = models.CharField(max_length=255, default='', blank=True)
    info = models.CharField(max_length=255, default='', blank=True)
    type = models.SmallIntegerField(choices=TYPES, default=1, blank=True)

    class Meta:
        app_label = 'web'

    def __str__(self):
        return self.code


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ('code', 'value', 'info', 'type')
    list_editable = ('value',)
    list_display_links = None
    actions = None
