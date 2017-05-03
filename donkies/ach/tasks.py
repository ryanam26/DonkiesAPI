import logging
from django.apps import apps
from django.conf import settings
from celery.decorators import periodic_task
from celery.task.schedules import crontab
from web.services.helpers import rs_singleton, production

rs = settings.REDIS_DB
logger = logging.getLogger('console')


# @periodic_task(run_every=crontab(hour='*/3'))
# @production(settings.PRODUCTION)
@rs_singleton(rs, 'PROCESS_STRIPE_TRANSFERS_IS_PROCESSING')
def process_transfers():
    TransferStripe = apps.get_model('ach', 'TransferStripe')
    TransferStripe.objects.process_transfers()


# @periodic_task(run_every=crontab(hour='*/4'))
# @production(settings.PRODUCTION)
@rs_singleton(rs, 'UPDATE_STRIPE_TRANSFERS_IS_PROCESSING')
def update_stripe_transfers():
    TransferStripe = apps.get_model('ach', 'TransferStripe')
    TransferStripe.objects.update_transfers()


# @periodic_task(run_every=crontab(minute=10, hour='*'))
# @production(settings.PRODUCTION)
@rs_singleton(rs, 'TRANSFER_TO_USER_IS_PROCESSING')
def transfer_user():
    TransferUser = apps.get_model('ach', 'TransferUser')
    TransferUser.objects.process_users()
