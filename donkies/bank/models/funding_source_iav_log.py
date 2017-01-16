from django.db import models
from django.contrib import admin
from django.apps import apps


class FundingSourceIAVLogManager(models.Manager):
    def create(self, account_id, dwolla_id):
        Account = apps.get_model('finance', 'Account')
        account = Account.objects.get(id=account_id)

        fs_log = self.model.objects.filter(
            account=account, dwolla_id=dwolla_id).first()
        if not fs_log:
            fs_log = self.model(account=account, dwolla_id=dwolla_id)
            fs_log.save()
        return fs_log


class FundingSourceIAVLog(models.Model):
    """
    This model is used as logs and fallback processing.

    When user creates funding source by IAV from frontend,
    funding source first created in Dwolla and then we need to
    create it in database.

    But if request to Dwolla API will fail, we won't be able
    to associate programmatically created funding source
    with finance account (if user has multiple accounts).

    Therefore each time when funding source is created,
    we save log info to this model.
    """
    account = models.ForeignKey('finance.Account')
    dwolla_id = models.CharField(max_length=255, unique=True)
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = FundingSourceIAVLogManager()

    class Meta:
        app_label = 'bank'
        verbose_name = 'funding source iav log'
        verbose_name_plural = 'funding source iav logs'
        ordering = ['-created_at']
        unique_together = ['account', 'dwolla_id']

    def __str__(self):
        return self.dwolla_id


@admin.register(FundingSourceIAVLog)
class FundingSourceIAVLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'account', 'dwolla_id', 'is_processed')
    actions = None
    list_display_links = None
