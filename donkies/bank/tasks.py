from django.apps import apps
from django.conf import settings
from django.db.models import Q
from celery.decorators import periodic_task
from celery.task.schedules import crontab
from web.services.helpers import rs_singleton

rs = settings.REDIS_DB


@periodic_task(run_every=crontab(minute='*'))
@rs_singleton(rs, 'CREATE_CUSTOMERS_IS_PROCESSING')
def create_customers():
    """
    Task that creates and inits customers in Dwolla.
    """
    Customer = apps.get_model('bank', 'Customer')
    # TODO  user__is_admin=False
    for c in Customer.objects.filter(created_at=None):
        Customer.objects.create_dwolla_customer(c.id)
        Customer.objects.init_dwolla_customer(c.id)


@periodic_task(run_every=crontab(minute='*'))
@rs_singleton(rs, 'CREATE_FUNDING_SOURCES_IS_PROCESSING')
def create_funding_sources():
    """
    Task that creates and inits funding sources in Dwolla.
    """
    FundingSource = apps.get_model('bank', 'FundingSource')
    for fs in FundingSource.objects.filter(created_at=None):
        FundingSource.objects.create_dwolla_funding_source(fs.id)
        FundingSource.objects.init_dwolla_funding_source(fs.id)


@periodic_task(run_every=crontab())
@rs_singleton(rs, 'MICRO_DEPOSITS_IS_PROCESSING')
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


@periodic_task(run_every=crontab())
@rs_singleton(rs, 'TRANSFERS_IS_PROCESSING')
def create_transfers():
    """
    Create transfers in bank.Transfer from finance.Transfer.
    """
    pass


@periodic_task(run_every=crontab())
@rs_singleton(rs, 'CREATE_DWOLLA_TRANSFERS_IS_PROCESSING')
def create_dwolla_transfers():
    """
    Process all transfers in bank.Transfer model.
    TODO: increase periodic interval on production.
    """
    Transfer = apps.get_model('bank', 'Transfer')
    for t in Transfer.objects.filter(dwolla_id=None):
        Transfer.objects.create_dwolla_transfer(t.id)


@periodic_task(run_every=crontab())
@rs_singleton(rs, 'UPDATE_DWOLLA_TRANSFERS_IS_PROCESSING')
def update_dwolla_transfers():
    """
    Updates status of transfers.
    (Can be also implemented by WebHooks API.)
    TODO: increase periodic interval on production.
    """
    Transfer = apps.get_model('bank', 'Transfer')
    for t in Transfer.objects.filter(dwolla_id__is_null=False, is_done=False):
        Transfer.objects.update_transfer(t.id)
