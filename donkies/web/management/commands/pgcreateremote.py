from django.core.management.base import BaseCommand
from django.conf import settings
from web.management.helpers import (
    get_remote_root_connection, get_remote_db_connection)


class Command(BaseCommand):
    help = 'Drop db and user and creates new db and user from scratch.'

    def handle(self, *args, **options):

        con, cur = get_remote_root_connection()

        cur.execute('drop database if exists {}'.format(settings.DB_NAME))
        # database for tests
        cur.execute('drop database if exists test_{}'.format(
            settings.DB_NAME))

        cur.execute('drop user if exists {}'.format(settings.DB_USER))

        cur.execute('create database {}'.format(settings.DB_NAME))
        cur.execute('create user {}'.format(settings.DB_USER))
        cur.execute("alter role {} password '{}'".format(
            settings.DB_USER, settings.DB_PASSWORD))

        self.stdout.write('New remote database initialized.')

        cur.execute('create database test_{}'.format(settings.DB_NAME))
        self.stdout.write('New remote test database initialized.')

        try:
            con, cur = get_remote_db_connection()
        except:
            self.stdout.write('Error: connection doesn\'t work.')
