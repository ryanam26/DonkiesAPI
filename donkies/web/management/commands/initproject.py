import shutil
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        l = [
            'web',
            'finance',
            'bank'
        ]
        for name in l:
            path = '{}/donkies/{}/migrations'.format(
                settings.BASE_DIR, name)
            shutil.rmtree(path, ignore_errors=True)

        print('Migrations have been removed.')
