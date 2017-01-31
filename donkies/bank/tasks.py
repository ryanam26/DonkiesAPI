from django.apps import apps
from django.conf import settings
from django.db.models import Q
from celery.decorators import periodic_task
from celery.task.schedules import crontab
from web.services.helpers import rs_singleton
from bank.services.dwolla_api import DwollaApi

rs = settings.REDIS_DB


@periodic_task(run_every=crontab(minute='*'))
@rs_singleton(rs, 'CREATE_CUSTOMERS_IS_PROCESSING')
def create_customers():
    """
    Task that creates and inits customers in Dwolla.
    """
    Customer = apps.get_model('bank', 'Customer')
    # TODO  user__is_admin=False
    for c in Customer.objects.filter(dwolla_id=None):
        Customer.objects.create_dwolla_customer(c.id)


@periodic_task(run_every=crontab(minute='*'))
@rs_singleton(rs, 'INIT_CUSTOMERS_IS_PROCESSING')
def initiate_customers():
    """
    Task that initiates created customers.
    """
    Customer = apps.get_model('bank', 'Customer')
    qs = Customer.objects.filter(dwolla_id__is_null=False, created_at=None)
    for c in qs:
        Customer.objects.initiate_dwolla_customer(c.id)


@periodic_task(run_every=crontab(minute='*/10'))
def process_sandbox_transfers():
    """
    For sandbox transfers.
    They are not processed by default.
    """
    dw = DwollaApi()
    dw.press_sandbox_button()


# Currently not used.
# @periodic_task(run_every=crontab(minute='*'))
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
