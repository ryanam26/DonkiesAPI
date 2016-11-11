import django
import os
import sys
import uuid

from os.path import abspath, dirname, join

path = abspath(join(dirname(abspath(__file__)), ".."))
sys.path.append(path)
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE', 'donkies.settings.development')
django.setup()


if __name__ == '__main__':
    from finance.services.atrium_api import AtriumApi
    a = AtriumApi()
    res = a.create_user(uuid.uuid4().hex)
    print(res)
