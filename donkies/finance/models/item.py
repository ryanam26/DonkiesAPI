from django.db import models
from django.contrib import admin
from django.contrib.postgres.fields import JSONField


class ItemManager(models.Manager):
    def create_item(self, user, api_data):
        d = api_data
        


class Item(models.Model):
    user = models.ForeignKey('web.User', related_name='items')
    institution = models.ForeignKey('Institution')
    plaid_id = models.CharField(max_length=255, unique=True)
    access_token = models.CharField(max_length=255, unique=True)
    request_id = models.CharField(max_length=100)
    webhook = models.CharField(
        max_length=50, null=True, default=None, blank=True)
    available_products = JSONField(null=True, default=None)
    billed_products = JSONField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, default=None, blank=True)

    objects = ItemManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'item'
        verbose_name_plural = 'items'
        ordering = ['-created_at']

    def __str__(self):
        return self.plaid_id


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        'plaid_id',
        'user',
        'institution',
        'request_id',
        'webhook',
        'available_products',
        'billed_products',
        'created_at',
        'updated_at',
    )
    readonly_fields = (
        'user',
        'institution',
        'plaid_id',
        'request_id',
        'webhook',
        'available_products',
        'billed_products',
        'created_at',
        'updated_at',
    )
