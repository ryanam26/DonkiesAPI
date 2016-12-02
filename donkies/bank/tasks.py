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
    Task that creates customers in Dwolla.
    """
    Customer = apps.get_model('bank', 'Customer')
    for c in Customer.objects.filter(is_created=False):
        Customer.objects.create_dwolla_customer(c.id)


@periodic_task(run_every=crontab(minute='*'))
@rs_singleton(rs, 'INIT_CUSTOMERS_IS_PROCESSING')
def init_customers():
    """
    Task that looks for created customers, but data about
    these customers hasn't been received yet.
    (When customer is created in Dwolla, there is no info about it.
    Info is available a bit later)
    """
    Customer = apps.get_model('bank', 'Customer')
    for c in Customer.objects.filter(is_created=True, dwolla_id=None):
        Customer.objects.init_dwolla_customer(c.id)
