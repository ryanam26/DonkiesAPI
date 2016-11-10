from django.db import models
from django.contrib import admin


class Challenge(models.Model):
    member = models.ForeignKey('Member')
    guid = models.CharField(max_length=100, unique=True)
    field_name = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    value = models.CharField(
        max_length=255, null=True, default=None, blank=True)
    is_responded = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.value:
            self.is_responded = True
        super().save(*args, **kwargs)

    class Meta:
        app_label = 'finance'
        verbose_name = 'challenge'
        verbose_name_plural = 'challenges'
        ordering = ['member']

    def __str__(self):
        return self.guid


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = (
        'member',
        'guid',
        'field_name',
        'label',
        'type',
        'value',
        'is_responded'
    )
