import logging
from django.apps import apps
from django.conf import settings
from django.db.models import Q
from celery.decorators import periodic_task
from celery.task.schedules import crontab
from donkies import capp
from web.services.helpers import rs_singleton, production
from bank.services.dwolla_api import DwollaApi

rs = settings.REDIS_DB
logger = logging.getLogger('console')


@capp.task
def create_customer(user_id):
    """
    Create customer in Model and Dwolla as soon as
    user completed profile.
    """
    Customer = apps.get_model('bank', 'Customer')
    User = apps.get_model('web', 'User')
    user = User.objects.get(id=user_id)
    if not hasattr(user, 'customer') or user.customer is None:
        c = Customer.objects.create_customer(user)
        Customer.objects.create_dwolla_customer(c.id)


@periodic_task(run_every=crontab(minute=10, hour='*'))
@rs_singleton(rs, 'CREATE_MODEL_CUSTOMERS_IS_PROCESSING')
def create_customers():
    """
    Task that creates customers in Customer model in case
    if regular task fails.
    """
    Customer = apps.get_model('bank', 'Customer')
    User = apps.get_model('web', 'User')
    for user in User.objects.filter(customer=None):
        if user.is_profile_completed:
            Customer.objects.create_customer(user)


@periodic_task(run_every=crontab(minute=20, hour='*'))
@production(settings.PRODUCTION)
@rs_singleton(rs, 'CREATE_DWOLLA_CUSTOMERS_IS_PROCESSING')
def create_dwolla_customers():
    """
    Task that creates customers in Dwolla in case if regular task fail.
    """
    Customer = apps.get_model('bank', 'Customer')
    for c in Customer.objects.filter(dwolla_id=None, user__is_admin=False):
        logger.debug('Task: create dwolla customer: {}'.format(c.email))
        Customer.objects.create_dwolla_customer(c.id)


@periodic_task(run_every=crontab(minute='*'))
@production(settings.PRODUCTION)
@rs_singleton(rs, 'INIT_DWOLLA_CUSTOMERS_IS_PROCESSING')
def initiate_dwolla_customers():
    """
    Task that initiates created customers.
    """
    Customer = apps.get_model('bank', 'Customer')
    qs = Customer.objects.filter(
        dwolla_id__is_null=False, created_at=None, user__is_admin=False)
    for c in qs:
        logger.debug('Task: initiate dwolla customer: {}'.format(c.email))
        Customer.objects.initiate_dwolla_customer(c.id)


@periodic_task(run_every=crontab(minute='*'))
@production(settings.PRODUCTION)
def update_customers():
    """
    TODO: increase interval on production
    """
    Customer = apps.get_model('bank', 'Customer')
    Customer.objects.update_customers()


@periodic_task(run_every=crontab(minute='*/10'))
@production(settings.PRODUCTION)
def process_sandbox_transfers():
    """
    For sandbox transfers.
    They are not processed by default.
    """
    dw = DwollaApi()
    dw.press_sandbox_button()


# Currently not used.
# @periodic_task(run_every=crontab(minute='*'))
# @production(settings.PRODUCTION)
# @rs_singleton(rs, 'CREATE_FUNDING_SOURCES_IS_PROCESSING')
def create_funding_sources():
    """
    Task that creates and inits funding sources in Dwolla.
    Manual creation using account_number and routing_number.
    """
    FundingSource = apps.get_model('bank', 'FundingSource')
    for fs in FundingSource.objects.filter(created_at=None):
        FundingSource.objects.create_dwolla_funding_source(fs.id)
        FundingSource.objects.init_dwolla_funding_source(fs.id)


# Currently not used.
# @periodic_task(run_every=crontab())
# @production(settings.PRODUCTION)
# @rs_singleton(rs, 'MICRO_DEPOSITS_IS_PROCESSING')
def micro_deposits():
    """
    Task that init micro-deposits and updates status.
    TODO: increase periodic interval on production to 1 hour.
    """
    FundingSource = apps.get_model('bank', 'FundingSource')
    qs = FundingSource.objects.filter(
        Q(md_status=FundingSource.PENDING) | Q(md_status=None),
        verification_type=FundingSource.MICRO_DEPOSITS
    )
    for fs in qs:
        FundingSource.objects.init_micro_deposits(fs.id)
        FundingSource.objects.update_micro_deposits(fs.id)
