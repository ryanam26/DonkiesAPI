from django.db import transaction
from django.contrib import admin
from django.db import models
from django.apps import apps
from django.conf import settings
from decimal import *
import dwollav2
from web.models import User


def get_founding_source(user):
    FundingSource = apps.get_model('finance', 'FundingSource')
    founding_instance = FundingSource.objects.filter(user=user).first()

    return founding_instance.funding_sources_url


def charge_application(amount, user):
    founding_source = get_founding_source(user)
    client = dwollav2.Client(id=settings.DWOLLA_ID_SANDBOX,
                             secret=settings.DWOLLA_SECRET_SANDBOX,
                             environment=settings.PLAID_ENV)
    app_token = client.Auth.client()
    root = app_token.get('/')
    account_url = root.body['_links']['account']['href']

    request_body = {
        '_links': {
            'source': {
                'href': founding_source
            },
            'destination': {
                'href': account_url
            }
        },
        'amount': {
            'currency': 'USD',
            'value': str(round(Decimal(amount), 2))
        },
        'metadata': {
            'donkie': 'user reached minimum value',
        }
    }

    transfer = app_token.post('transfers', request_body)
    return transfer.headers['location']


class TransferCalculation(models.Model):
    user = models.ForeignKey(User, related_name='user_calulations')
    roundup_sum = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=0)
    total_roundaps = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=0)
    min_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=5)

    def save(self, roundup=None, *args, **kwargs):
        if roundup is not None:
            self.roundup_sum += round(Decimal(roundup), 2)
            self.total_roundaps += round(Decimal(roundup), 2)

            if self.roundup_sum >= self.min_amount:
                self.roundup_sum = self.roundup_sum - self.min_amount
                charge_application(self.min_amount, self.user)

        super().save(*args, **kwargs)


@admin.register(TransferCalculation)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'roundup_sum',
        'total_roundaps',
        'min_amount',
    )

