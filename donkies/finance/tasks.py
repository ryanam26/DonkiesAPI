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
