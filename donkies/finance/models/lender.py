from django.db import models
from django.contrib import admin


class LenderManager(models.Manager):
    def create_lender(self, user, institution, account_number):
        if not institution.is_manual:
            raise ValueError('Institution should be manual')

        qs = self.model.objects.filter(user=user, institution=institution)
        if qs.exists():
            return qs.first()

        l = self.model(
            user=user,
            institution=institution,
            account_number=account_number)
        l.save()
        return l


class Lender(models.Model):
    """
    Only manual institutions can be foreign keys.
    """
    user = models.ForeignKey('web.User')
    institution = models.ForeignKey('Institution')
    account_number = models.CharField(
        max_length=100, default='', blank=True)

    objects = LenderManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'lender'
        verbose_name_plural = 'lenders'
        ordering = ['user']

    def __str__(self):
        return str(self.id)


@admin.register(Lender)
class LenderAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'institution',
        'account_number'
    )
