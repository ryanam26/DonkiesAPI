from django.apps import apps
from donkies import capp

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
