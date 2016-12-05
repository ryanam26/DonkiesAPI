from django.apps import apps
from django.conf import settings
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
    for c in Customer.objects.filter(created_at=None, user__is_admin=False):
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
