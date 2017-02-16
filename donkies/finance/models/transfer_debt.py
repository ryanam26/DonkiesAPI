import decimal
from django.db import models
from django.contrib import admin
from django.apps import apps


class TransferDebtManager(models.Manager):
    def create_debts(self, tu_id):
        """
        Process TransferUser to TransferDebt debt accounts
        accordingly to share.
        """
        TransferUser = apps.get_model('finance', 'TransferUser')
        tu = TransferUser.objects.get(id=tu_id)

        Account = apps.get_model('finance', 'Account')

        user = tu.user
        qs = Account.objects.debt_accounts().filter(member__user=user)

        l = []
        sum = 0
        for account in qs:
            t_debt = self.model(
                account=account, tu=tu, share=account.transfer_share)

            target = tu.amount * account.transfer_share / 100
            t_debt.amount = target.quantize(decimal.Decimal('.01'))

            sum += t_debt.amount
            l.append(t_debt)

        # Fix 0.01 precision
        if sum != tu.amount:
            t_debt = l[-1]
            if sum > tu.amount:
                diff = sum - tu.amount
                t_debt.amount -= diff
            else:
                diff = tu.amount - sum
                t_debt.amount += diff

        # Checking
        sum = 0
        for t_debt in l:
            sum += t_debt.amount
        assert sum == tu.amount  # should never be error, because fixed

        for t_debt in l:
            if t_debt.amount > 0:
                t_debt.save()


class TransferDebt(models.Model):
    """
    After all data have been processed to TransferDebt model,
    send payment to user's debt accounts.
    In current implementations by cheques manually.
    """
    account = models.ForeignKey(
        'Account',
        related_name='transfers_user',
        help_text='Debt account.')
    tu = models.ForeignKey(
        'TransferUser', help_text='TransferUser transfer')
    share = models.IntegerField(help_text='Current share on processing date.')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    processed_at = models.DateTimeField(null=True, default=None, blank=True)
    is_processed = models.BooleanField(default=False)

    objects = TransferDebtManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'transfer debt'
        verbose_name_plural = 'transfers debt'
        ordering = ['-processed_at']

    def __str__(self):
        return str(self.id)


@admin.register(TransferDebt)
class TransferDebtAdmin(admin.ModelAdmin):
    list_display = (
        'account',
        'tu',
        'share',
        'amount',
        'processed_at',
        'is_processed'
    )
