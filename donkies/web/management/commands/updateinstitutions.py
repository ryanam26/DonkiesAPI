from django.core.management.base import BaseCommand
from finance.tasks import update_institutions


class Command(BaseCommand):
    def handle(self, *args, **options):
        update_institutions.delay()
        print('Request to update institutions has been sent.')
