import logging
from django.apps import apps
from django.conf import settings
from donkies import capp
from celery.decorators import periodic_task
from celery.task.schedules import crontab
from web.services.helpers import rs_singleton, production

rs = settings.REDIS_DB
logger = logging.getLogger('console')


@capp.task
def process_plaid_webhooks(data):
    """
    Plaid sends webhook signal to API url.
    API view run this celery task.
    """
    PlaidWebhook = apps.get_model('finance', 'PlaidWebhook')
    PlaidWebhook.objects.process_webhook(data)


@capp.task
def fetch_transactions(access_token):
    """
    Used when new item is created.
    On production transactions can be fetched by webhook.
    But on development can't get webhook.
    """
    Transaction = apps.get_model('finance', 'Transaction')
    Transaction.objects.create_or_update_transactions(access_token)


# --- Transfers

@periodic_task(run_every=crontab(minute='*/15', hour='*'))
@production(settings.PRODUCTION)
@rs_singleton(rs, 'PROCESS_ROUNDUPS_IS_PROCESSING')
def process_roundups():
    TransferPrepare = apps.get_model('finance', 'TransferPrepare')
    TransferPrepare.objects.process_roundups()
