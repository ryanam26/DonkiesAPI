from django.db import models
from django.contrib import admin
from django.core.exceptions import ValidationError


class LinkDebtManager(models.Manager):
    def create_link(self, user, account, share):
        """
        The sum of share of all accounts for particular user
        should be always equal 100%. When new link created,
        proportionally reduce share of existing accounts for particular user.
        """
        if share > 100:
            raise ValidationError('Share can not exceed 100%')

        qs = self.model.objects.filter(user=user)
        if not qs:
            share = 100
            ld = self.model(user=user, account=account, share=share)
            ld.save()
            return ld

        ld_new = self.model(user=user, account=account, share=share)
        l = list(qs)
        l.append(ld_new)

        working = True
        while working:
            for ld in l:
                if not ld.pk:
                    continue
                ld.share -= 1
                if self.get_share_sum(l) == 100:
                    working = False
                    break

        for ld in l:
            ld.save()

        ld_new.save()
        return ld_new

    def get_share_sum(self, l):
        """
        Input: list of LinkDebt objects.
        Returns: sum of share.
        """
        total = 0
        for ld in l:
            total += ld.share
        return total


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
        unique_together = ['user', 'account']

    def __str__(self):
        return '{}: {}'.format(self.account.name, self.share)


@admin.register(LinkDebt)
class LinkDebtAdmin(admin.ModelAdmin):
    list_display = ('user', 'account', 'share')
