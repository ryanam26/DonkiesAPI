from django.core.management.base import BaseCommand
from django.conf import settings
from web.management.helpers import get_local_root_connection


class Command(BaseCommand):
    help = 'Drop local db'

    def handle(self, *args, **options):

        con, cur = get_local_root_connection()

        cur.execute('drop database if exists {}'.format(settings.DB_NAME))
        con.close()
        self.stdout.write('Local db has been dropped.')
