import logging
from django.apps import apps
from django.conf import settings
from donkies import capp
from celery.decorators import periodic_task
from celery.task.schedules import crontab

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


@capp.task
def fetch_history_transactions():
    """
    Fetch recursively one by one until finish.
    """
    Transaction = apps.get_model('finance', 'Transaction')
    FetchTransactions = apps.get_model('finance', 'FetchTransactions')

    ft = FetchTransactions.objects.filter(is_processed=False).first()
    if ft is not None:
        Transaction.objects.create_or_update_transactions(
            ft.item.access_token,
            start_date=ft.start_date, end_date=ft.end_date)
        ft.is_processed = True
        ft.save()
        fetch_history_transactions.delay()


@capp.task
def fetch_account_numbers(account_id):
    """
    Fetch account_number and routing_number for account.
    """
    Account = apps.get_model('finance', 'Account')
    account = Account.objects.get(id=account_id)
    account.set_account_numbers()


@periodic_task(run_every=crontab(minute=10, hour=2))
def update_institutions():
    """
    Once a day.
    """
    if not settings.PRODUCTION:
        return

    Institution = apps.get_model('finance', 'Institution')
    Institution.objects.update_institutions()


# --- Transfers

# @periodic_task(run_every=crontab(minute='*/15', hour='*'))
# @rs_singleton(rs, 'PROCESS_ROUNDUPS_IS_PROCESSING')
def process_roundups():
    TransferPrepare = apps.get_model('finance', 'TransferPrepare')
    TransferPrepare.objects.process_roundups()
