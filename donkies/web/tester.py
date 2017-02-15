import django
import os
import sys

from os.path import abspath, dirname, join
from django.apps import apps

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

    def temp(self):
        from finance.services.atrium_api import AtriumApi
        Member = apps.get_model('finance', 'Member')

        a = AtriumApi()
        for user in a.get_users():
            for member in Member.objects.get_atrium_members(user.guid):
                print(member.status, member.name)
                if member.status == Member.HALTED:
                    a.aggregate_member(member.user_guid, member.guid)


if __name__ == '__main__':
    t = Tester()
    t.temp()
