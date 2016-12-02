from django.apps import apps
from django.conf import settings
from celery.decorators import periodic_task
from celery.task.schedules import crontab


@periodic_task(run_every=crontab(minute='*'))
def create_customers():
    """
    Task that creates customers in Dwolla.
    """
    Customer = apps.get_model('bank', 'Customer')
    IS_PROCESSING = 'CREATE_CUSTOMERS_IS_PROCESSING'
    rs = settings.REDIS_DB

    if rs.get(IS_PROCESSING):
        return

    rs.set(IS_PROCESSING, 'true')
    rs.expire(IS_PROCESSING, 1800)

    for c in Customer.objects.filter(is_created=False):
        Customer.objects.create_dwolla_customer(c.id)

    rs.delete(IS_PROCESSING)


@periodic_task(run_every=crontab(minute='*'))
def init_customers():
    """
    Task that looks for created customers, but data about
    these customers hasn't been received yet.
    (When customer is created in Dwolla, there is no info about it.
    Info is available a bit later)
    """
    Customer = apps.get_model('bank', 'Customer')
    IS_PROCESSING = 'INIT_CUSTOMERS_IS_PROCESSING'
    rs = settings.REDIS_DB

    if rs.get(IS_PROCESSING):
        return

    rs.set(IS_PROCESSING, 'true')
    rs.expire(IS_PROCESSING, 1800)

    for c in Customer.objects.filter(is_created=True, dwolla_id=None):
        Customer.objects.init_dwolla_customer(c.id)

    rs.delete(IS_PROCESSING)
