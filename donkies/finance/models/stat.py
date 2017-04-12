from django.db import models
from django.contrib import admin
from django.db.models import Sum
from django.apps import apps


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

    def get_json(self, user_id):
        return {
            'amount_to_stripe': self.get_to_stripe_amount(user_id),
            'amount_to_user': self.get_to_user_amount(user_id),
            'amount_available': self.get_available_amount(user_id),
            'payments': self.get_payments_count(user_id)
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
