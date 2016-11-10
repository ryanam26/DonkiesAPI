from django.db import models
from django.contrib import admin


class Transaction(models.Model):

    class Meta:
        app_label = 'finance'
        verbose_name = ''
        verbose_name_plural = ''
        ordering = ['']

    def __str__(self):
        return self.


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('',)
