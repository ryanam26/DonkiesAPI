import decimal
from django.db import models
from django.contrib import admin
from django.apps import apps
from django.db.models import Sum
from django.db import transaction
from django.utils import timezone


class TransferUserManager(models.Manager):
    def process(self):
        TransferDonkies = apps.get_model('finance', 'TransferDonkies')
        users = TransferDonkies.objects.get_date_queryset()\
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
        TransferDonkies = apps.get_model('finance', 'TransferDonkies')

        if not self.can_process_user(user_id):
            return

        tu = self.model(user_id=user_id)
        tu.save()
        for td in TransferDonkies.objects.get_user_queryset(user_id):
            td.is_processed_to_user = True
            td.processed_at = timezone.now()
            td.save()

            tu.items.add(td)

        tu.create_debts()

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
        TransferDonkies = apps.get_model('finance', 'TransferDonkies')
        User = apps.get_model('web', 'User')

        if not TransferDonkies.objects.get_user_queryset(user_id):
            return False

        Account = apps.get_model('finance', 'Account')
        qs = Account.objects.debt_accounts().filter(
            member__user_id=user_id)
        if not qs:
            return False

        user = User.objects.get(id=user_id)
        if not user.is_auto_transfer:
            return False

        res = TransferDonkies.objects.get_user_queryset(
            user_id).aggregate(Sum('amount'))
        if res['amount__sum'] < user.minimum_transfer_amount:
            return False

        return True


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
        if self.cached_amount is not None\
                and self.cached_amount > 0 and is_update is False:
            return self.cached_amount
        res = self.items.all().aggregate(Sum('amount'))
        return res['amount__sum']

    def update_cached_amount(self):
        amount = self.amount(is_update=True)
        self.cached_amount = amount

    def create_debts(self):
        """
        Process TransferUser to TransferDebt debt accounts
        accordingly to share.
        At the time when TransferUser created itself.
        """
        Account = apps.get_model('finance', 'Account')
        TransferDebt = apps.get_model('finance', 'TransferDebt')

        user = self.user
        qs = Account.objects.debt_accounts().filter(member__user=user)

        l = []
        sum = 0
        for account in qs:
            t_debt = TransferDebt(
                account=account, tu=self, share=account.transfer_share)

            target = self.amount * account.transfer_share / 100
            t_debt.amount = target.quantize(decimal.Decimal('.01'))

            sum += t_debt.amount
            l.append(t_debt)

        # Fix 0.01 precision
        if sum != self.amount:
            t_debt = l[-1]
            if sum > self.amount:
                diff = sum - self.amount
                t_debt.amount -= diff
            else:
                diff = self.amount - sum
                t_debt.amount += diff

        # Checking
        sum = 0
        for t_debt in l:
            sum += t_debt.amount
        assert sum == self.amount  # should never be error, because fixed

        for t_debt in l:
            if t_debt.amount > 0:
                t_debt.save()


@admin.register(TransferUser)
class TransferUserAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'user',
        'amount'
    )
