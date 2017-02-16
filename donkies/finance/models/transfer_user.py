import datetime
from django.db import models
from django.contrib import admin
from django.apps import apps
from django.db.models import Sum
from django.db import transaction
from django.utils import timezone


class TransferUserManager(models.Manager):
    def process(self):
        users = self.get_queryset()\
            .order_by('account__member__user_id')\
            .values_list('account__member__user_id', flat=True)\
            .distinct()

        for user_id in users:
            self.process_user(user_id)

    @transaction.atomic
    def process_user(self, user_id):
        """
        1) Create TransferUser instance.
        2) Add to instance.items all TransferDonkies items.
        3) All TransferDonkies items set:
            is_processed_to_user = True
            processed_at = now
        4) Create TransferDebt instances accordingly to share.
        """
        TransferDebt = apps.get_model('finance', 'TransferDebt')

        if not self.can_process_user(user_id):
            return

        tu = self.model(user_id=user_id)
        tu.save()
        for td in self.get_user_queryset():
            td.is_processed_to_user = True
            td.processed_at = timezone.now()
            td.save()

            tu.items.add(td)

        TransferDebt.objects.create_debts(tu.id)

    def can_process_user(self, user_id):
        """
        Returns bool.
        1) Can not process if aggregated payments not ready yet.
        2) Can not process if user doesn't have debt accounts.
        3) Can not process if user didn't set "is_auto_transfer"
        4) Can not process if user minimum_transfer_amount
           less than aggregated amount.
        """
        Account = apps.get_model('finance', 'Account')
        User = apps.get_model('web', 'User')

        if not self.get_user_queryset(user_id):
            return False

        Account = apps.get_model('finance', 'Account')
        qs = Account.objects.debt_accounts().filter(
            member__user_id=user_id)
        if not qs:
            return False

        user = User.objects.get(id=user_id)
        if not user.is_auto_transfer:
            return False

        res = self.get_user_queryset().aggregate(Sum('amount'))
        if res['amount__sum'] < user.minimum_transfer_amount:
            return False

        return True

    def get_queryset(self):
        """
        Returns queryset for available payments.
        """
        TransferDonkies = apps.get_model('finance', 'TransferDonkies')
        return TransferDonkies.objects.filter(
            is_processed_to_user=False,
            is_sent=True,
            sent_at__lt=self.get_date())

    def get_user_queryset(self, user_id):
        """
        Returns queryset for available payments
        for particular user.
        """
        return self.get_queryset().filter(
            account__member__user_id=user_id)

    def get_date(self):
        """
        Returns date, for filter TransferDonkies that less
        than that date.

        If today's date is less than 15th, returns 1st day of last month.
        If today's date is more or equal 15th, returns
        1st day of current month.
        """
        today = datetime.date.today()
        if today.day < 15:
            dt = today.replace(day=1) - datetime.timedelta(days=1)
            return dt.replace(day=1)
        return today.replace(day=1)


class TransferUser(models.Model):
    """
    Donkies LLC holds user's money.
    All transfers from user's debit accounts to TransferDonkies
    are stored in TransferDonkies model.

    On 15th of current month, funds can be transferred to TransferUser
    model, if user set "is_auto_transfer" and if total amount more than
    "minimum_transfer_amount".

    TransferUser model delegates funds to TransferDebt model
    to user's debt accounts accordingly to share.
    """
    user = models.ForeignKey('web.User', related_name='transfers')
    cached_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True,
        default=None, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    items = models.ManyToManyField('TransferDonkies')

    objects = TransferUserManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'transfer user'
        verbose_name_plural = 'transfers user'
        ordering = ['-created_at']

    def __str__(self):
        return str(self.id)

    @property
    def amount(self, is_update=False):
        if self.cached_amount > 0 and is_update is False:
            return self.cached_amount
        res = self.items.all().aggregate(Sum('amount'))
        return res['amount__sum']

    def update_cached_amount(self):
        amount = self.amount(is_update=True)
        self.cached_amount = amount


@admin.register(TransferUser)
class TransferUserAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'user',
        'amount'
    )
