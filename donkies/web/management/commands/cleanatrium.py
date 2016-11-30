from django.core.management.base import BaseCommand
from web.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        User.objects.clean_atrium()
