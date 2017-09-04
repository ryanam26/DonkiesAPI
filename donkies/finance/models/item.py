import uuid
from django.db import models
from django.contrib import admin
from django.db import transaction
from django.contrib.postgres.fields import JSONField
from django.conf import settings
from django.apps import apps
from finance.services.plaid_api import PlaidApi

from web.models import ActiveModel, ActiveManager


class ItemManager(ActiveManager):
    def create_item_by_public_token(self, user, public_token):
        """
        1) Item created on Plaid by Plaid Link.
        2) Plaid Link returned public_token.
        2) Exchange public_token for access token.
        3) Get Item by access_token.
        4) Create Item in Model.
        """
        pa = PlaidApi()
        access_token = pa.exchange_public_token(public_token)
        data = pa.get_item(access_token)
        return Item.objects.create_item(user, data)

    def create_item_by_data(self, user, data):
        pa = PlaidApi()
        public_token = data.get('public_token')

        try:
            access_token = pa.exchange_public_token(user, public_token)

            context = pa.get_item(access_token)
            context.update(data)
            item = Item.objects.create_item(user, context)
        except Exception as e:
            raise e

        return item

    def create_item(self, user, d):
        """
        api_data - Plaid's API response
        """
        Institution = apps.get_model('finance', 'Institution')
        access_token = d['access_token']
        institution = Institution.objects.get_or_create_institution(
            d['institution_id'])

        item = self.model(
            user=user,
            institution=institution,
            plaid_id=d['item_id'],
            access_token=access_token,
            webhook=d.get('webhook', None),
            billed_products=d.get('billed_products', None),
            available_products=d.get('available_products', None)
        )
        try:
            item.save()
        except Exception as e:
            raise e

        return item

    def delete_item(self, id):
        """
        Delete item from Plaid.
        Set item, accounts and transactions to is_active=False
        """
        item = self.model.objects.get(id=id)
        if settings.TESTING is False:
            if item.plaid_id:
                pa = PlaidApi()
                pa.delete_item(item.access_token)
        self.change_active(item.id, False)

    @transaction.atomic
    def change_active(self, item_id, is_active):
        """
        is_active = True - besides item itself,
                    activates also all accounts.
        is_active = False - besides item itself,
                    deactivates also all accounts.
        """
        Account = apps.get_model('finance', 'Account')
        for account in Account.objects.filter(item_id=item_id):
            Account.objects.change_active(account.id, is_active)
        self.model.objects.filter(id=item_id).update(is_active=is_active)

    def clean_plaid(self):
        """
        Used for production debugging.
        Delete all items in Plaid.
        """
        User = apps.get_model('web', 'User')
        pa = PlaidApi()
        for item in self.model.objects.filter(plaid_id__isnull=False):
            pa.delete_item(item.access_token)
        User.objects.filter(is_admin=False).delete()


class Item(ActiveModel):
    """
    If Item doesn't have plaid_id, it is internal Item
    that doesn't exist in Plaid.
    """
    user = models.ForeignKey('web.User', related_name='items')
    institution = models.ForeignKey('Institution')
    guid = models.CharField(max_length=50, unique=True)
    plaid_id = models.CharField(
        max_length=255, unique=True, null=True, default=None)
    access_token = models.CharField(
        max_length=255, unique=True, null=True, default=None)
    webhook = models.CharField(
        max_length=50, null=True, default=None, blank=True)
    available_products = JSONField(null=True, default=None)
    billed_products = JSONField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, default=None, blank=True)
    pause = models.BooleanField(default=False, blank=True)

    objects = ItemManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'item'
        verbose_name_plural = 'items'
        ordering = ['-created_at']

    def __str__(self):
        return self.plaid_id

    def save(self, *args, **kwargs):
        if not self.pk:
            self.guid = uuid.uuid4().hex
        super().save(*args, **kwargs)

    def pause_on(self, *args, **kwargs):
        self.pause = True
        self.save()

    def pause_off(self, *args, **kwargs):
        self.pause = False
        self.save()


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        'plaid_id',
        'user',
        'institution',
        'webhook',
        'available_products',
        'billed_products',
        'created_at',
        'updated_at',
        'access_token',
        'pause',
    )
    readonly_fields = (
        'user',
        'guid',
        'institution',
        'plaid_id',
        'webhook',
        'available_products',
        'billed_products',
        'created_at',
        'updated_at',
        'pause',
    )
