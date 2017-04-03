from django.db import models
from django.contrib import admin
from django.db import transaction
from django.contrib.postgres.fields import JSONField
from django.apps import apps
from finance.services.plaid_api import PlaidApi
from web.models import ActiveModel, ActiveManager


class ItemManager(ActiveManager):
    def create_item(self, user, api_data):
        """
        api_data - Plaid's API response
        """
        Institution = apps.get_model('finance', 'Institution')
        request_id = api_data['request_id']
        access_token = api_data['access_token']
        d = api_data['item']
        institution = Institution.objects.get_or_create_institution(
            d['institution_id'])

        item = self.model(
            user=user,
            institution=institution,
            request_id=request_id,
            plaid_id=d['item_id'],
            access_token=access_token,
            webhook=d.get('webhook', None),
            billed_products=d.get('billed_products', None),
            available_products=d.get('available_products', None)
        )
        item.save()
        return item

    def delete_item(self, item_id):
        """
        Delete item from Plaid.
        Set item, accounts and transactions to is_active=False
        """
        item = self.model.objects.get(id=item_id)
        pa = PlaidApi()

    @transaction.atomic
    def change_active(self, member_id, is_active):
        """
        is_active = True - besides member itself,
                    activates also all accounts.
        is_active = False - besides member itself,
                    deactivates also all accounts.
        """
        Account = apps.get_model('finance', 'Account')
        for account in Account.objects.filter(member_id=member_id):
            Account.objects.change_active(account.id, is_active)
        self.model.objects.filter(id=member_id).update(is_active=is_active)

        self.change_active(member.id, False)

    def clean_plaid(self):
        """
        Used for production debugging.
        Delete all items in Plaid.
        """
        User.objects.filter(is_admin=False).delete()
        a = AtriumApi()
        for d in a.get_users():
            a.delete_user(d['guid'])



class Item(ActiveModel):
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
