from django.db import models
from django.contrib import admin


class Transaction(models.Model):
    account = models.ForeignKey('Account')
    guid = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, default=None)
    check_number = models.IntegerField(null=True, default=None)
    category = models.CharField(max_length=255, null=True, default=None)
    created_at = models.DateTimeField(null=True, default=None)
    description = models.CharField(max_length=3000, null=True, default=None)
    is_bill_paid = models.NullBooleanField()
    is_direct_deposit = models.NullBooleanField()
    is_expense = models.NullBooleanField()
    is_fee = models.NullBooleanField()
    is_income = models.NullBooleanField()
    is_overdraft_fee = models.NullBooleanField()
    is_payroll_advance = models.NullBooleanField()
    latitude = models.DecimalField(
        max_digits=10, decimal_places=6, null=True, default=None)
    longitude = models.DecimalField(
        max_digits=10, decimal_places=6, null=True, default=None)
    memo = models.CharField(max_length=255, null=True, default=None)
    merchant_category_code = models.IntegerField(null=True, default=None)
    original_description = models.CharField(
        max_length=3000, null=True, default=None)
    posted_at = models.DateTimeField(null=True, default=None)
    status = models.CharField(max_length=50)
    top_level_category = models.CharField(
        max_length=255, null=True, default=None)
    transacted_at = models.DateTimeField(null=True, default=None)
    type = models.CharField(max_length=50)
    updated_at = models.DateTimeField(null=True, default=None)

    class Meta:
        app_label = 'finance'
        verbose_name = 'transaction'
        verbose_name_plural = 'transactions'
        ordering = ['account']

    def __str__(self):
        return self.guid


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    pass
