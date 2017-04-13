from django.core.management.base import BaseCommand
from django.conf import settings
from finance.models import Institution


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        Creates manual institutions from institutions.txt
        """
        path = '{}/donkies/finance/management/commands/institutions.txt'\
            .format(settings.BASE_DIR)
        data = open(path).read()
        l = data.split('\n\n')
        for line in l:
            tup = line.split('\n')
            assert len(tup) == 4

            i = Institution()
            i.name, i.box, i.address, i.link = tup
            i.is_manual = True
            i.save()
