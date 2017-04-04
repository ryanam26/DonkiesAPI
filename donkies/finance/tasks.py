import datetime
import logging
from django.utils import timezone
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
    PlaidWebhook = apps.get_model('finance', 'PlaidWebhook')
    PlaidWebhook.objects.process_webhook(data)


# --- Transfers to Dwolla

@periodic_task(run_every=crontab(minute='*/15', hour='*'))
@production(settings.PRODUCTION)
@rs_singleton(rs, 'PROCESS_ROUNDUPS_IS_PROCESSING')
def process_roundups():
    TransferPrepare = apps.get_model('finance', 'TransferPrepare')
    TransferPrepare.objects.process_roundups()


@periodic_task(run_every=crontab(minute='*/10'))
@production(settings.PRODUCTION)
@rs_singleton(rs, 'PROCESS_PREPARE_IS_PROCESSING')
def process_prepare():
    TransferDonkies = apps.get_model('finance', 'TransferDonkies')
    TransferDonkies.objects.process_prepare()


@periodic_task(run_every=crontab(minute='*/10'))
@production(settings.PRODUCTION)
@rs_singleton(rs, 'INITIATE_DWOLLA_TRANSFERS_IS_PROCESSING')
def initiate_dwolla_transfers():
    TransferDonkies = apps.get_model('finance', 'TransferDonkies')
    for tds in TransferDonkies.objects.filter(is_initiated=False):
        TransferDonkies.objects.initiate_dwolla_transfer(tds.id)


@periodic_task(run_every=crontab(minute='*/10'))
@production(settings.PRODUCTION)
@rs_singleton(rs, 'UPDATE_DWOLLA_TRANSFERS_IS_PROCESSING')
def update_dwolla_transfers():
    """
    Updates status of Donkies transfers.
    """
    TransferDonkies = apps.get_model('finance', 'TransferDonkies')
    qs = TransferDonkies.objects.filter(
        is_initiated=True, is_sent=False, is_failed=False)
    for tds in qs:
        TransferDonkies.objects.update_dwolla_transfer(tds.id)


@periodic_task(run_every=crontab(minute='*/10'))
@production(settings.PRODUCTION)
@rs_singleton(rs, 'UPDATE_DWOLLA_FAILURE_CODES_IS_PROCESSING')
def update_dwolla_failure_codes():
    """
    Updates failure codes in TransferDonkies.
    """
    TransferDonkies = apps.get_model('finance', 'TransferDonkies')
    qs = TransferDonkies.objects.filter(is_failed=True, failure_code=None)
    for tds in qs:
        TransferDonkies.objects.update_dwolla_failure_code(tds.id)


@periodic_task(run_every=crontab(minute=0, hour='*/6'))
@production(settings.PRODUCTION)
def reinitiate_dwolla_transfers():
    """
    Reinitiate failed transfers with "R01" failure_code after
    24 hours.
    """
    TransferDonkies = apps.get_model('finance', 'TransferDonkies')
    dt = timezone.now() - datetime.timedelta(hours=24)
    TransferDonkies.objects\
        .filter(is_failed=True, failure_code='R01', updated_at__lt=dt)\
        .update(
            is_initiated=False,
            is_failed=False,
            failure_code=None,
            status=None
        )


@periodic_task(run_every=crontab(minute=10, hour='*'))
@production(settings.PRODUCTION)
@rs_singleton(rs, 'TRANSFER_USER_IS_PROCESSING')
def transfer_user():
    TransferUser = apps.get_model('finance', 'TransferUser')
    TransferUser.objects.process()
