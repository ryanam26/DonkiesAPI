from faker import Faker
from django.conf import settings
from django.core.management.base import BaseCommand
from finance.services.atrium_api import AtriumApi
from finance.tasks import update_user
from finance.models import Member
from web.models import User


class Command(BaseCommand):
    """
    Production Atrium test users.
    """
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
            u.address1 = Faker().street_address()
            u.city = Faker().city()
            u.date_of_birth = '1980-01-01'
            u.state = Faker().state_abbr()
            u.postal_code = Faker().postalcode()
            u.ssn = Faker().ssn()
            u.save()

            if u.guid:
                self.create_member(u.guid)
                # Update Atrium accounts and transactions
                update_user(u.id)

        print('Test users have been created.')
