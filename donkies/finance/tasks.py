import datetime
import logging
from atrium.errors import NotFoundError
from django.utils import timezone
from django.apps import apps
from django.conf import settings
from donkies import capp
from celery.decorators import periodic_task
from celery.task.schedules import crontab
from web.services.helpers import rs_singleton, production

rs = settings.REDIS_DB
logger = logging.getLogger('console')

# The number of attempts to get member before exit.
MAX_ATTEMPTS = 10


@periodic_task(run_every=crontab(minute=20, hour='*'))
@rs_singleton(rs, 'CREATE_ATRIUM_USER_IS_PROCESSING', exp=300)
def create_atrium_users():
    """
    Task that creates atrium users, if for any reason they wasn't
    created by regular task.

    TODO: on production change to run once per hour.
    While development, run every minute.
    """
    User = apps.get_model('web', 'User')
    for user in User.objects.filter(guid=None, is_admin=False):
        logger.debug('Task: creating atrium user: {}'.format(user.email))
        User.objects.create_atrium_user(user.id)


@capp.task
def create_atrium_user(user_id):
    User = apps.get_model('web', 'User')
    user = User.objects.get(id=user_id)
    User.objects.create_atrium_user(user.id)


@capp.task
def get_member(member_id, attempt=0):
    """
    Task will call atrium API until receive finished status.
    Or delete member from Atrium and database.
    """
    Account = apps.get_model('finance', 'Account')
    Member = apps.get_model('finance', 'Member')
    Challenge = apps.get_model('finance', 'Challenge')

    if attempt > MAX_ATTEMPTS:
        # Delete member
        Member.objects.real_delete_member(member_id)
        return

    member = Member.objects.get(id=member_id)
    logger.debug('Task: resume member.')

    try:
        am = Member.objects.get_atrium_member(member)
    except NotFoundError:
        return
    except Exception as e:
        logger.exception(e)
        attempt += 1
        return get_member.apply_async(
            args=[member_id],
            kwargs={'attempt': attempt},
            countdown=5)

    status = am.status

    if status not in Member.FINISHED_STATUSES:
        attempt += 1
        return get_member.apply_async(
            args=[member_id],
            kwargs={'attempt': attempt},
            countdown=5)

    # If status is HALTED, it means some server error
    # or unavailability. Aggregate member again.
    if status == Member.HALTED:
        Member.objects.aggregate_member(member.guid)
        return get_member.apply_async(
            args=[member_id],
            kwargs={'attempt': attempt},
            countdown=10)

    # If status is DENIED, remove member.
    # We need to create it again, or bugs can be happen in Atrium.
    if status == Member.DENIED:
        Member.objects.real_delete_member(member_id)
        return

    # If status is CHALLENGED, create challenges for member in database
    if status == Member.CHALLENGED:
        Challenge.objects.create_challenges(am)

    # Accounts should be available before COMPLETED status
    # saved to db.
    if status == Member.COMPLETED:
        l = Account.objects.get_atrium_accounts(member.user.guid)
        Account.objects.create_or_update_accounts(member.user.guid, l)

    member.status = status
    member.aggregated_at = am.aggregated_at
    member.successfully_aggregated_at = am.successfully_aggregated_at
    member.save()

    # Update user's accounts and transactions.
    update_user.apply_async(args=[member.user.id], countdown=10)


@capp.task
def update_user(user_id):
    """
    Updates accounts and transactions of particular user.
    """
    Account = apps.get_model('finance', 'Account')
    Transaction = apps.get_model('finance', 'Transaction')
    User = apps.get_model('web', 'User')
    user = User.objects.get(id=user_id)
    if user.is_admin:
        return

    logger.debug('Task: update atrium user: {}'.format(user.email))

    l = Account.objects.get_atrium_accounts(user.guid)
    Account.objects.create_or_update_accounts(user.guid, l)
    logger.debug('Task: accounts updated.')

    l = Transaction.objects.get_atrium_transactions(user.guid)
    Transaction.objects.create_or_update_transactions(user.guid, l)
    logger.debug('Task: transactions updated.')


@periodic_task(run_every=crontab(minute=0, hour='*'))
@rs_singleton(rs, 'USER_DATA_IS_PROCESSING', exp=3600)
def update_users_data():
    """
    Runs every hour.
    Celery task, that updates all users, who have members
    with COMPLETED status.
    """
    Member = apps.get_model('finance', 'Member')
    qs = Member.objects.active()\
        .filter(status=Member.COMPLETED, user__is_admin=False)\
        .values_list('user_id', flat=True).distinct()
    for user_id in qs:
        update_user(user_id)


@periodic_task(run_every=crontab(minute=0, hour=0))
def update_institutions():
    """
    Updates institutions.
    """
    Institution = apps.get_model('finance', 'Institution')
    Institution.objects.update_list()

    # Credentials in db not needed in current implementation.
    # Institution.objects.update_credentials()


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
