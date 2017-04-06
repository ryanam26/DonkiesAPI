import json
import logging
from django.db import models
from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from django.apps import apps
from django.conf import settings

logger = logging.getLogger('app')


class PlaidWebhookManager(models.Manager):
    """
    Plaid send different webhooks to app.
    Save all webhooks to model and process them.

    Webhooks code (type):
    INITIAL_UPDATE (TRANSACTIONS)
    HISTORICAL_UPDATE (TRANSACTIONS)
    DEFAULT_UPDATE (TRANSACTIONS)
    REMOVED_TRANSACTIONS (TRANSACTIONS)
    WEBHOOK_UPDATE_ACKNOWLEDGED (ITEM)
    ERROR (ITEM)
    """

    def process_webhook(self, data):
        Item = apps.get_model('finance', 'Item')
        try:
            item = Item.objects.get(plaid_id=data.get('item_id'))
        except Item.DoesNotExist:
            msg = 'Webhook, incorrect item_id: {}'.format(
                json.dumps(data))
            logger.error(msg)

        code = data['webhook_code']
        method_name = 'process_{}'.format(code.lower())
        method = getattr(self, method_name, None)
        if method is not None:
            method(item, data)

    def create_webhook(self, item, data):
        pw = PlaidWebhook(item=item)
        pw.code = data.get('webhook_code')
        pw.type = data.get('webhook_type')
        pw.error = data.get('error')
        pw.data = data
        pw.save()
        return pw

    def process_initial_update(self, item, data):
        """
        Update transactions.
        """
        Transaction = apps.get_model('finance', 'Transaction')
        self.create_webhook(item, data)
        if settings.TESTING is False:
            Transaction.objects.create_or_update_transactions(
                item.access_token)

    def process_historical_update(self, item, data):
        """
        Update transactions.
        """
        Transaction = apps.get_model('finance', 'Transaction')
        self.create_webhook(item, data)
        if settings.TESTING is False:
            Transaction.objects.create_or_update_transactions(
                item.access_token)

    def process_default_update(self, item, data):
        """
        Update transactions.
        """
        Transaction = apps.get_model('finance', 'Transaction')
        self.create_webhook(item, data)
        if settings.TESTING is False:
            Transaction.objects.create_or_update_transactions(
                item.access_token)

    def process_removed_transactions(self, item, data):
        """
        Removed transactions.
        """
        self.create_webhook(item, data)

    def process_webhook_update_acknowledged(self, item, data):
        """
        Item is updated.
        """
        self.create_webhook(item, data)

    def process_error(self, item, data):
        """
        Error. Each error has code.
        """
        self.create_webhook(item, data)


class PlaidWebhook(models.Model):
    item = models.ForeignKey('Item', related_name='items')
    type = models.CharField(max_length=50)
    code = models.CharField(max_length=50)
    error = JSONField(null=True, default=None)
    data = JSONField(null=True, default=None)
    debug_info = models.TextField(null=True, default=None, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = PlaidWebhookManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'webhook'
        verbose_name_plural = 'webhooks'
        ordering = ['-created_at']

    def __str__(self):
        return '{} -> {}'.format(self.type, self.code)


@admin.register(PlaidWebhook)
class PlaidWebhookAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'item',
        'code',
        'type',
        'error',
        'data'
    )
    readonly_fields = (
        'created_at',
        'code',
        'type',
        'item',
        'error',
        'data',
    )
