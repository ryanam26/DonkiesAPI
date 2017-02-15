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
        User = apps.get_model('web', 'User')
        Member = apps.get_model('finance', 'Member')

        user = User.objects.get(email='alex@donkies.co')
        member = Member.objects.filter(
            user=user, institution__code='wells_fargo').first()

        res = Member.objects.get_atrium_member(member)
        print(res)

        res = Member.objects.read_atrium_member(member)
        print(res)


if __name__ == '__main__':
    t = Tester()
    # t.temp()
    print(t.get_atrium_users())
