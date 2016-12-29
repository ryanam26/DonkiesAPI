import subprocess
from django.core.management.base import BaseCommand
from django.conf import settings
from web.management.helpers import (
    get_local_pg_root_password, get_remote_pg_root_password)


class Command(BaseCommand):
    help = 'Download remote db and fill local db.'

    def handle(self, *args, **options):
        local_dump_path = settings.BASE_DIR + '/db.dump'

        passwd_local = get_local_pg_root_password()
        passwd_remote = get_remote_pg_root_password()

        cmd = 'ssh vlad@{} '.format(settings.SERVER_IP)
        cmd += 'PGPASSWORD="{}" '.format(passwd_remote)
        cmd += 'pg_dump -U postgres {} -f db.dump --format=c'.format(
            settings.DB_NAME)
        subprocess.call(cmd, shell=True)
        print('Remote dump has been created.')

        cmd = 'scp vlad@{}:db.dump {}'.format(
            settings.SERVER_IP, local_dump_path)
        subprocess.call(cmd, shell=True)
        print('Remote dump has been copied to localhost.')

        cmd = 'ssh vlad@{} rm db.dump'.format(settings.SERVER_IP)
        subprocess.call(cmd, shell=True)
        print('Remote dump has been deleted.')

        cmd = 'PGPASSWORD="{}" '.format(passwd_local)
        cmd += 'pg_restore -d {} -U {} {}'.format(
            settings.DB_NAME, settings.DB_USER, local_dump_path)
        subprocess.call(cmd, shell=True)
        print('Local db has been filled.')
