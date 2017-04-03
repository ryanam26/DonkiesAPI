from django.core.management.base import BaseCommand
from finance.services.plaid_api import PlaidApi
from finance.models import Category


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        Creates Plaid categories.
        """
        pa = PlaidApi()
        data = pa.get_categories()
        for d in data['categories']:
            Category.objects.create_category(d)
        print('Categories have been created')
