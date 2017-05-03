"""
Fetch history transactions.
2 weeks range for the year back from "item" date.
"""

import datetime
from django.db import transaction
from django.db import models
from django.contrib import admin


class FetchTransactionsManager(models.Manager):
    def create(self, item, start_date, end_date):
        ft = self.model(
            item_id=item.id,
            start_date=start_date,
            end_date=end_date
        )
        ft.save()
        return ft

    @transaction.atomic
    def create_all(self, item):
        """
        Create two weeks intervals for item.
        Start is year ago from item.created_at
        """
        start_date = item.created_at - datetime.timedelta(days=365)
        end_date = start_date + datetime.timedelta(days=14)

        while end_date < item.created_at:
            self.create(item, start_date, end_date)
            start_date = start_date + datetime.timedelta(days=14)
            end_date = end_date + datetime.timedelta(days=14)


class FetchTransactions(models.Model):
    item = models.ForeignKey('Item')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_processed = models.BooleanField(default=False)

    objects = FetchTransactionsManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'fetch transactions'
        verbose_name_plural = 'fetch transactions'
        ordering = ['id']

    def __str__(self):
        return str(self.id)


@admin.register(FetchTransactions)
class FetchTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'item',
        'start_date',
        'end_date',
        'is_processed',
    )
