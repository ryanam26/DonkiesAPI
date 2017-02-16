from django.core.management.base import BaseCommand
from finance.services.generator import Generator


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Starting to generate data...')
        g = Generator()
        g.run()
