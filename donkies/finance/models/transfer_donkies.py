from django.db import models
from django.contrib import admin
from django.apps import apps
from django.db import transaction
from django.db.models import Sum


class TransferDonkiesManager(models.Manager):
    def process_prepare(self):
        """
        Called by celery scheduled task.
        Process TransferPrepare to TransferDonkies model.
        """
        TransferPrepare = apps.get_model('finance', 'TransferPrepare')

        users = TransferPrepare.objects.filter(is_processed=False)\
            .order_by('account__member__user_id')\
            .values_list('account__member__user_id', flat=True)\
            .distinct()

        for user_id in users:
            self.process_prepare_user(user_id)

    @transaction.atomic
    def process_prepare_user(self, user_id):
        """
        If user has not set funding source yet, do not move
        funds from TransferPrepare to TransferDonkies.
        """
        TransferPrepare = apps.get_model('finance', 'TransferPrepare')
        User = apps.get_model('web', 'User')

        user = User.objects.get(id=user_id)
        fs = user.get_funding_source_account()
        if fs is None:
            return

        sum = TransferPrepare.objects.filter(
            is_processed=False,
            account__member__user=user)\
            .aggregate(Sum('roundup'))['roundup__sum']

        TransferPrepare.objects.filter(
            is_processed=False,
            account__member__user=user).update(is_processed=True)

        tds = self.model(account=fs, amount=sum)
        tds.save()


class TransferDonkies(models.Model):
    """
    If user set funding source debit account, transfer all
    amount for particular user from TransferPrepare to this model.
    Then send money to Donkeys LLC (via Dwolla)

    As soon as money has been sent to Donkeys - set is_sent = True
    Check by API receiving money to Donkeys LLC account and as
    soon as money received - set is_received = True

    Process received amount to user debt's accounts accordingly to share
    to TransferUser model.
    """
    account = models.ForeignKey(
        'Account',
        related_name='transfers_donkies',
        help_text='Funding source debit account.')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, default=None, blank=True)
    received_at = models.DateTimeField(null=True, default=None, blank=True)
    processed_at = models.DateTimeField(null=True, default=None, blank=True)
    is_sent = models.BooleanField(
        default=False, help_text='Money sent to Donkies LLC')
    is_received = models.BooleanField(
        default=False, help_text='Money received by Donkies LLC')
    is_processed_to_user = models.BooleanField(
        default=False, help_text='Funds processed to TransferUser model.')

    objects = TransferDonkiesManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'transfer donkies'
        verbose_name_plural = 'transfers donkies'
        ordering = ['-created_at']

    def __str__(self):
        return str(self.id)


@admin.register(TransferDonkies)
class TransferDonkiesAdmin(admin.ModelAdmin):
    list_display = (
        'account',
        'amount',
        'created_at',
        'sent_at',
        'received_at',
        'processed_at',
        'is_sent',
        'is_received',
        'is_processed_to_user'
    )
    readonly_fields = (
        'account',
        'amount',
        'created_at',
        'sent_at',
        'received_at',
        'processed_at',
        'is_sent',
        'is_received',
        'is_processed_to_user'
    )

    def has_delete_permission(self, request, obj=None):
        return False
