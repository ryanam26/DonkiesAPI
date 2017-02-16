import decimal
from django.db import models
from django.contrib import admin
from django.apps import apps


class TransferUserManager(models.Manager):
    def process_to_model(self):
        """
        !!! REFACTORING REQUIRED

        Process all transfers to TransferUser model,
        that have been sent from TransferDonkies model to Donkies LLC.
        All processed items in TransferDonkies
        is_processed_to_user should be set to True.
        """
        TransferDonkies = apps.get_model('finance', 'TransferDonkies')

        qs = TransferDonkies.objects.filter(
            is_sent=True, is_processed_to_user=False)

        for td in qs:
            self.process_td_to_model(td)

    def process_td_to_model(self, td):
        """
        Process TransferDonkies item to TransferUser debt accounts.
        """
        Account = apps.get_model('finance', 'Account')

        user = td.account.member.user
        qs = Account.objects.debt_accounts().filter(member__user=user)

        l = []
        sum = 0
        for account in qs:
            tu = self.model(
                account=account, td=td, share=account.transfer_share)

            target = td.amount * account.transfer_share / 100
            tu.amount = target.quantize(decimal.Decimal('.01'))

            sum += tu.amount
            l.append(tu)

        if not l:
            return

        # Fix 0.01 precision
        if sum != td.amount:
            tu = l[-1]
            if sum > td.amount:
                diff = sum - td.amount
                tu.amount -= diff
            else:
                diff = td.amount - sum
                tu.amount += diff

        # Checking
        sum = 0
        for tu in l:
            sum += tu.amount
        assert sum == td.amount  # should never be error, because fixed

        for tu in l:
            if tu.amount > 0:
                tu.save()

        td.is_processed_to_user = True
        td.save()


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
    def amount(self):
        return '0'


@admin.register(TransferUser)
class TransferUserAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'user',
        'amount'
    )
