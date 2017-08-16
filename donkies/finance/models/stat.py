import datetime
from django.db import models
from django.contrib import admin
from django.db.models import Sum
from django.apps import apps
from bank.services.dwolla_api import DwollaApi
from decimal import *


class StatManager(models.Manager):
    def get_collected_roundup(self, user_id):
        """
        Roundup total, that collected
        but not sent to Donkies yet.
        """
        Transaction = apps.get_model('finance', 'Transaction')
        TransferPrepare = apps.get_model('finance', 'TransferPrepare')
        TransferStripe = apps.get_model('ach', 'TransferStripe')

        sum1 = Transaction.objects\
            .filter(account__item__user_id=user_id, is_processed=False)\
            .aggregate(Sum('roundup'))['roundup__sum']

        sum2 = TransferPrepare.objects\
            .filter(account__item__user_id=user_id, is_processed=False)\
            .aggregate(Sum('roundup'))['roundup__sum']

        sum3 = TransferStripe.objects\
            .filter(account__item__user_id=user_id, paid=False)\
            .aggregate(Sum('amount'))['amount__sum']

        sum1 = sum1 if sum1 is not None else 0
        sum2 = sum2 if sum2 is not None else 0
        sum3 = sum3 if sum3 is not None else 0
        return sum1 + sum2 + sum3

    def get_to_stripe_amount(self, user_id):
        """
        Returns total roundup transferred to Stripe.
        """
        TransferStripe = apps.get_model('ach', 'TransferStripe')
        sum = TransferStripe.objects\
            .filter(account__item__user_id=user_id, paid=True)\
            .aggregate(Sum('amount'))['amount__sum']
        if sum is not None:
            return sum
        return 0

    def get_to_user_amount(self, user_id):
        """
        Returns total roundup transferred to User.
        """
        TransferDebt = apps.get_model('ach', 'TransferDebt')
        sum = TransferDebt.objects\
            .filter(account__item__user_id=user_id, is_processed=True)\
            .aggregate(Sum('amount'))['amount__sum']
        if sum is not None:
            return sum
        return 0

    def get_available_amount(self, user_id):
        """
        Dwolla implementation.
        Returns total amount available to transfer.
        """
        TransferStripe = apps.get_model('ach', 'TransferStripe')
        qs = TransferStripe.objects.get_user_queryset(user_id)
        sum = qs\
            .aggregate(Sum('amount'))['amount__sum']
        if sum is not None:
            return sum
        return 0

    def get_payments_count(self, user_id):
        TransferDebt = apps.get_model('ach', 'TransferDebt')
        return TransferDebt.objects\
            .filter(account__item__user_id=user_id, is_processed=True)\
            .count()

    def get_roundup_since_signup(self, user_id):
        Transaction = apps.get_model('finance', 'Transaction')
        User = apps.get_model('web', 'User')

        user = User.objects.get(id=user_id)
        sum = Transaction.objects.filter(
            account__item__user=user, date__gte=user.created_at
        ).aggregate(Sum('roundup'))['roundup__sum']

        if not sum:
            return 0

        return sum

    def get_daily_average_roundup(self, user_id):
        """
        Average daily roundup  since first available transaction.
        Returns total roundup/num_days
        """
        Transaction = apps.get_model('finance', 'Transaction')
        sum = Transaction.objects\
            .filter(account__item__user_id=user_id)\
            .aggregate(Sum('roundup'))['roundup__sum']

        if not sum:
            return 0

        first_transaction = Transaction.objects.filter(
            account__item__user_id=user_id).earliest('date')

        dt = first_transaction.date
        delta = datetime.date.today() - dt
        return sum / delta.days

    def get_monthly_average_roundup(self, user_id):
        return self.get_daily_average_roundup(user_id) * 30

    def get_yearly_average_roundup(self, user_id):
        return self.get_daily_average_roundup(user_id) * 365

    def get_funds_in_coinstash(self, user_id):
        User = apps.get_model('web', 'User')

        user = User.objects.get(id=user_id)
        dw = DwollaApi()

        customer_url = "{}customers/{}/funding-sources".format(
            dw.get_api_url(), user.dwolla_verified_url.split('/')[-1]
        )

        funding_sources = dw.token.get(customer_url)
        balance_url = None

        for i in funding_sources.body['_embedded']['funding-sources']:
            if "balance" in i['_links'].keys():
                balance_url = i['_links']['balance']['href']

        balance = dw.token.get(balance_url)

        return balance.body['balance']

    def get_json(self, user_id):
        return {
            'roundup_since_signup': self.get_roundup_since_signup(user_id),
            'monthly_average_roundup': self.get_monthly_average_roundup(user_id),
            'yearly_average_roundup': self.get_yearly_average_roundup(user_id),
            'funds_in_coinstash': self.get_funds_in_coinstash(user_id)
        }


class Stat(models.Model):
    """
    In future consider periodically cache all stat
    to database and serve from database.
    """

    objects = StatManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'stat'
        verbose_name_plural = 'stat'
        ordering = ['id']

    def __str__(self):
        return str(self.id)


@admin.register(Stat)
class StatAdmin(admin.ModelAdmin):
    list_display = ('id',)
