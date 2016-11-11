from django.conf import settings
from django.core.management.base import BaseCommand
from web.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        User.objects.create_user(
            settings.TEST_USER_EMAIL,
            settings.TEST_USER_PASSWORD)
        print('Test user has been created.')
