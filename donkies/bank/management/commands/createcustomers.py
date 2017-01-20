from django.core.management.base import BaseCommand
from faker import Faker
from bank.models import Customer
from web.models import User


class Command(BaseCommand):
    """
    Create customers in database for all existing users.
    On init project.
    """
    def create_customer(self, user):
        c = Customer(user=user)
        user.address1 = Faker().street_address()
        user.city = Faker().city()
        user.date_of_birth = '1980-01-01'
        user.state = Faker().state_abbr()
        user.postal_code = Faker().postalcode()
        user.ssn = Faker().ssn()
        user.save()
        c.save()

    def set_names(self):
        """
        Set first name and last name for users.
        Required by Dwolla.
        """
        for user in User.objects.all():
            if not user.first_name:
                user.first_name = Faker().first_name()
            if not user.last_name:
                user.last_name = Faker().last_name()
            user.save()

    def handle(self, *args, **options):
        for user in User.objects.all():
            self.create_customer(user)

        self.set_names()
        print('Customers have been created.')
