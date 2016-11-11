from django.core.management.base import BaseCommand
from django.conf import settings
from web.management.helpers import get_remote_root_connection


class Command(BaseCommand):
    help = 'Drop remote db'

    def handle(self, *args, **options):

        con, cur = get_remote_root_connection()

        cur.execute('drop database if exists {}'.format(settings.DB_NAME))
        con.close()
        self.stdout.write('Remote db has been dropped.')
