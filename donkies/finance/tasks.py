from django.apps import apps
from donkies import capp


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
    Task will call atrium API until get finished status.
    """
    Member = apps.get_model('finance', 'Member')
    if attempt > 20:
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

    member.status = status
    member.aggregated_at = am.aggregated_at
    member.successfully_aggregated_at = am.successfully_aggregated_at
    member.save()
