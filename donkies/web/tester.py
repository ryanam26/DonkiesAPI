import django
import os
import sys

from os.path import abspath, dirname, join
from django.apps import apps
from django.db.models import Q

path = abspath(join(dirname(abspath(__file__)), '..'))
sys.path.append(path)
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE', 'donkies.settings.development')
django.setup()


class Tester:
    def send_email(self):
        from web.tasks import send_email
        send_email()

    def get_atrium_users(self):
        from finance.services.atrium_api import AtriumApi

        a = AtriumApi()
        return a.get_users()

    def resume_halted(self):
        from finance.services.atrium_api import AtriumApi
        Member = apps.get_model('finance', 'Member')

        a = AtriumApi()
        for user in a.get_users():
            for member in Member.objects.get_atrium_members(user.guid):
                print(member.status, member.name)
                if member.status == Member.HALTED:
                    a.aggregate_member(member.user_guid, member.guid)

    def clean(self):
        """
        Accurate!!!
        """
        return
        from finance.services.atrium_api import AtriumApi
        User = apps.get_model('web', 'User')

        emails = ['alex@donkies.co', 'a@a.com']
        good_guids = User.objects.filter(
            email__in=emails).values_list('guid', flat=True)

        a = AtriumApi()
        for user in a.get_users():
            if user.guid not in good_guids:
                a.delete_user(user.guid)

        User.objects.filter(~Q(email__in=emails)).delete()

if __name__ == '__main__':
    t = Tester()
