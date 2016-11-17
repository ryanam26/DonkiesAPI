from django.apps import apps
from django.conf import settings
from donkies import capp
from celery.decorators import periodic_task
from celery.task.schedules import crontab


# The number of attempts to get member  before exit.
# In testing environment 20 is more than enought.
# In production probably need to be increased.
MAX_ATTEMPTS = 20


@capp.task
def create_atrium_user(user_id):
    """
    TODO: case when request to atrium fails, rerun task.
          create periodic task, that handle not created cases.
    """
    User = apps.get_model('web', 'User')
    user = User.objects.get(id=user_id)
    User.objects.create_atrium_user(user.id)


@capp.task
def get_member(member_id, attempt=0):
    """
    Task will call atrium API until receive finished status.
    """
    Member = apps.get_model('finance', 'Member')
    Challenge = apps.get_model('finance', 'Challenge')

    if attempt > MAX_ATTEMPTS:
        return

    try:
        member = Member.objects.get(id=member_id)
    except Member.DoesNotExist:
        return

    try:
        am = Member.objects.get_atrium_member(member)
    except:
        attempt += 1
        return get_member.apply_async(
            args=[member_id], kwargs={'attempt': attempt}, countdown=2)

    status = am.status

    if status not in Member.FINISHED_STATUSES:
        attempt += 1
        return get_member.apply_async(
            args=[member_id], kwargs={'attempt': attempt}, countdown=2)

    # If status is CHALLENGED, create challenges for member in database
    if status == Member.CHALLENGED:
        Challenge.objects.create_challenges(am)

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

    res = Account.objects.get_atrium_accounts(user.guid)
    l = res['accounts']

    Account.objects.create_accounts(user.guid, l)
    print('Accounts created.')

    res = Transaction.objects.get_atrium_transactions(user.guid)
    l = res['transactions']

    Transaction.objects.create_transactions(user.guid, l)
    print('Transactions created.')


@periodic_task(run_every=crontab(minute=0, hour='*'))
def update_users_data():
    """
    Runs every hour.
    Celery task, that updates all users, who have members
    with COMPLETED status.
    """
    Member = apps.get_model('finance', 'Member')
    IS_PROCESSING = 'USER_DATA_IS_PROCESSING'
    rs = settings.REDIS_DB

    if rs.get(IS_PROCESSING):
        return

    rs.set(IS_PROCESSING, 'true')
    rs.expire(IS_PROCESSING, 3000)

    qs = Member.objects.filter(status=Member.COMPLETED)\
        .values_list('user_id', flat=True).distinct()
    for user_id in qs:
        update_user(user_id)

    rs.delete(IS_PROCESSING)


@periodic_task(run_every=crontab(minute=0, hour='*/6'))
def update_institutions():
    """
    Updates institutions and their credentials.
    """
    Institution = apps.get_model('finance', 'Institution')
    Institution.objects.update_list()
    Institution.objects.update_credentials()
