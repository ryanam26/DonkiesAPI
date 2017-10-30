import logging
from django.apps import apps
from django.conf import settings
from django.utils import timezone
from donkies import capp
from celery.decorators import periodic_task
from celery.task.schedules import crontab
from web.services.helpers import round_to_prev5
from bank.services.dwolla_api import DwollaApi
from decimal import *
from datetime import datetime

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
@periodic_task(run_every=crontab(minute=0, hour=17))
def take_monthly_fee():
    dwa = DwollaApi()
    root = dwa.token.get(url='/')
    dwolla_account = root.body['_links']['account']['href']
    Customer = apps.get_model('bank', 'Customer')
    account_token = dwa.client.Token(access_token = dwa.token.access_token, refresh_token = dwa.token.access_token)
    for customer in Customer.objects.exclude(
        user__is_paused=True).exclude(
            user__is_closed_account=True).exclude(
                user__active_days=30):
        customer.user.active_days+=1
        customer.user.save()
    for customer in Customer.objects.exclude(
        user__is_paused=True).exclude(
            user__is_closed_account=True).filter(
                user__active_days=30):
        result = dwa.get_funding_sources(customer.dwolla_id)[0]
        customer_source_url = result['_links']['self']['href']
        customer_balance_id = result[0]['id']
        customer_balance = dwa.get_funding_source_balance(customer_balance_id)['balance']['value']
        if float(customer_balance) < 1.99:
            request_body = {
                '_links': {
                    'source': {
                    'href': customer_source_url
                        },
                    'destination': {
                    'href': dwolla_account
                        }
                    },
                'amount': {
                    'currency': 'USD',
                    'value': '1.99'
                    }
                }
            transfer = account_token.post('transfers', request_body)
            customer.user.active_days = 0
            customer.user.save()
        else:
            logger.info("Not enough money to fee")
        logger.info("Got fee from customer{}".format(customer.dwolla_id))

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


@periodic_task(run_every=crontab(minute=10))
def create_roundup_alerts():
    """
    Create alerts when roundup is more than 5, 10, 15
    for each user since signup.
    """
    User = apps.get_model('web', 'User')
    Alert = apps.get_model('web', 'Alert')
    Stat = apps.get_model('finance', 'Stat')

    for user in User.objects.all():
        print(user)
        amount = Stat.objects.get_roundup_since_signup(user.id)
        amount = round_to_prev5(amount)

        if amount > 5 and amount > user.last_alert_amount:
            message = 'User {} reach next roundup step: ${}'.format(
                user.email, amount)

            Alert.objects.create_alert(
                Alert.EMAIL, 'roundup alert', message)

            user.last_alert_amount = amount
            user.save()


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


def transfer_money(amount, funding_source):
    TransferCalculation = apps.get_model('finance', 'TransferCalculation')
    FundingSource = apps.get_model('finance', 'FundingSource')

    dw = DwollaApi()

    destination = settings.DWOLLA_TEMP_BUSINESS_ACCOUNT

    request_body = {
        '_links': {
            'source': {
                'href': funding_source
            },
            'destination': {
                'href': destination
            }
        },
        'amount': {
            'currency': 'USD',
            'value': amount
        }
    }
    try:
        transfer = dw.token.post('transfers', request_body)
        print(transfer.headers['location'])
        trans_calc = TransferCalculation.objects.get(
            user=FundingSource.objects.get(
                funding_sources_url=funding_source
            ).user
        )
        trans_calc.applied_funds = Decimal(amount)
        trans_calc.save()
    except Exception as error:
        logger.info(error)


@periodic_task(run_every=crontab(0, 0, day_of_month='28'))
def charge_dwoll_buisness():
    """
    Transfer money to dwolla buisness
    on the 28 day of every month.
    """
    FundingSource = apps.get_model('finance', 'FundingSource')
    Account = apps.get_model('finance', 'Account')
    User = apps.get_model('web', 'User')

    fi = Account.objects.filter(is_primary=True).values_list(
        'item__funding_items', flat=True
    ).distinct()  # id funding sources

    fs = FundingSource.objects.filter(pk__in=fi).exclude(
        funding_sources_url=None
    ).distinct().values_list('user', 'funding_sources_url')  # user and url

    for pk, url in fs:
        amount = User.objects.get(pk=pk).user_calulations.values_list(
            'total_in_stash_account', flat=True
        ).first()

        if amount == 0 or amount is None:
            continue
        transfer_money(amount, url)


@periodic_task(run_every=crontab(minute=0, hour='*/3'))
def process_transfers():
    TransferBalance = apps.get_model('finance', 'TransferBalance')
    TransferBalance.objects.update_status_transaction()
