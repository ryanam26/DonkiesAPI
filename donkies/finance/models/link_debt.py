from django.db import models
from django.contrib import admin


class LinkDebtManager(models.Manager):
    def create(self, user, account, share):
        """
        The sum of share of all accounts for particular user
        should be always equal 100%. When new link created,
        we reduce share of existing accounts for particular user.
        """


class LinkDebt(models.Model):
    user = models.ForeignKey('web.User')
    account = models.ForeignKey('Account', help_text='Debt account')
    share = models.IntegerField(default=0)

    objects = LinkDebtManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'link debt'
        verbose_name_plural = 'link debts'
        ordering = ['user']

    def __str__(self):
        return '{}: {}'.format(self.account.name, self.share)


@admin.register(LinkDebt)
class LinkDebtAdmin(admin.ModelAdmin):
    list_display = ('user', 'account', 'share')
