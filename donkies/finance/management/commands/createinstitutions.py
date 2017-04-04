from django.core.management.base import BaseCommand
from finance.models import Institution


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        Fetch all institutions from Plaid and save to db.
        """
        Institution.objects.fetch_all_institutions()
        print('Institutions have been created')
