import decimal
from django.db import models
from django.contrib import admin
from django.apps import apps


class TransferUserManager(models.Manager):
    def process_to_model(self):
        """
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
    As soon as Donkies LLC received money from user to bank account,
    process all data from TransferDonkies to TransferUser.
    Received amount should be splitted between all user's Debt accounts
    accordingly to share.

    After all data have been processed to TransferUser, send payment to user's
    debt accounts.

    In current implementations by cheques manually.
    """
    account = models.ForeignKey(
        'Account',
        related_name='transfers_user',
        help_text='Debt account.')
    td = models.ForeignKey(
        'TransferDonkies', help_text='Related TransferDonkies amount')
    share = models.IntegerField(help_text='Current share on processing date.')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, default=None, blank=True)
    is_processed = models.BooleanField(default=False)

    objects = TransferUserManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'transfer user'
        verbose_name_plural = 'transfers user'
        ordering = ['-created_at']

    def __str__(self):
        return str(self.id)


@admin.register(TransferUser)
class TransferUserAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'account',
        'td',
        'share',
        'amount',
        'processed_at',
        'is_processed'
    )
