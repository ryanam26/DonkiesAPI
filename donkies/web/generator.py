"""Generate initial data"""

import django
import os
import sys
import string
import random
from django.db import transaction
from os.path import abspath, dirname, join

path = abspath(join(dirname(abspath(__file__)), ".."))
sys.path.append(path)
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE', 'donkies.settings.development')
django.setup()

from web import models


class Generator:
    def randstring(self, len):
        s = string.ascii_lowercase
        return ''.join(random.sample(s, len))


if __name__ == '__main__':
    g = Generator()
