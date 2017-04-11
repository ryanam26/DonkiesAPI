from django.db import models
from django.contrib import admin
from django.contrib.postgres.fields import JSONField


class ChargeLog(models.Model):
    """
    Save Stripe's charge object when create Charge in Stripe.
    """
    account = models.ForeignKey('finance.Account')
    data = JSONField(null=True, default=None, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'ach'
        verbose_name = 'charge log'
        verbose_name_plural = 'charge logs'
        ordering = ['-created_at']

    def __str__(self):
        return str(self.id)


@admin.register(ChargeLog)
class ChargeLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'account', 'data')
    readonly_fields = ('created_at', 'account', 'data')
