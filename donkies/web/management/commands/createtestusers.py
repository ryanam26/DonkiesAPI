from django.conf import settings
from django.core.management.base import BaseCommand
from finance.services.atrium_api import AtriumApi
from finance.models import Member
from web.models import User


class Command(BaseCommand):
    def create_member(self, user_guid):
        """
        Fetch members from Atrium for exisiting Atrium users
        and save to database.
        """
        a = AtriumApi()
        res = a.get_members(user_guid)
        for d in res['members']:
            Member.objects.create_member(d)

    def handle(self, *args, **options):
        for d in settings.TEST_USERS:
            u = User.objects.create_user(
                d['email'], d['password'], guid=d['guid'])
            u.is_confirmed = True
            u.first_name = d['first_name']
            u.last_name = d['last_name']
            u.save()

            if u.guid:
                self.create_member(u.guid)

        print('Test users have been created.')
