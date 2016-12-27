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
        user.address1 = fake.address()[:50]
        user.city = fake.city()
        user.date_of_birth = '1980-01-01'
        user.state = fake.state_abbr()
        user.postal_code = fake.postalcode()
        user.ssn = fake.ssn()
        user.save()
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
