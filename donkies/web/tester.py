import django
import os
import sys

from os.path import abspath, dirname, join

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


if __name__ == '__main__':
    t = Tester()
    # from finance.services.atrium_api import AtriumApi
    # a = AtriumApi()
    # for d in a.get_users()['users']:
    #     print(d['guid'])
