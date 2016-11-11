import django
import os
import sys

from os.path import abspath, dirname, join

path = abspath(join(dirname(abspath(__file__)), ".."))
sys.path.append(path)
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE', 'donkies.settings.development')
django.setup()


if __name__ == '__main__':
    from finance.models import Credentials
    from finance.services.atrium_api import AtriumApi
    a = AtriumApi()

    Credentials.objects.update_all_credentials('chase')
    for obj in Credentials.objects.all():
        print(obj.__dict__)
