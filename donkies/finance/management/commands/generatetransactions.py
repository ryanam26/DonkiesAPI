from django.core.management.base import BaseCommand
from finance.services.generator import Generator


class Command(BaseCommand):
    """
    Generates fake transactions for admin user.
    Works only on "DEV" Atrium environment.
    Do not run on "PROD" environment.
    """
    def handle(self, *args, **options):
        g = Generator()
        g.run()
