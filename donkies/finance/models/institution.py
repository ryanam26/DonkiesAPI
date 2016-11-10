from django.db import models
from django.contrib import admin


class Institution(models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    sort = models.IntegerField(default=0)

    class Meta:
        app_label = 'finance'
        verbose_name = 'institution'
        verbose_name_plural = 'institutions'
        ordering = ['sort', 'name']

    def __str__(self):
        return self.code


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'url', 'sort')
    list_editable = ('sort',)
