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
        fake = Faker()

        c = Customer(user=user)
        c.address1 = fake.address()[:50]
        c.city = fake.city()
        c.date_of_birth = '1980-01-01'
        c.state = fake.state_abbr()
        c.postal_code = fake.postalcode()
        c.ssn = fake.ssn()
        c.save()

    def set_names(self):
        """
        Set first name and last name for users.
        Required by Dwolla.
        """
        fake = Faker()

        for user in User.objects.all():
            if not user.first_name:
                user.first_name = fake.first_name()
            if not user.last_name:
                user.last_name = fake.last_name()
            user.save()

    def handle(self, *args, **options):
        for user in User.objects.all():
            self.create_customer(user)

        self.set_names()
        print('Customers have been created.')
