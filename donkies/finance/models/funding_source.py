from web.models import ActiveModel
from django.db import models
from django.contrib import admin
from finance.models.item import Item
from web.models.user import User


class FundingSource(ActiveModel):
    user = models.ForeignKey(User, related_name='funding_sources_user')
    funding_sources_url = models.CharField(max_length=255, blank=True,
                                           null=True)
    item = models.ForeignKey(Item, related_name='funding_items', blank=True,
                             null=True)


@admin.register(FundingSource)
class FundingSourceAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'funding_sources_url',
        'item',
    )
