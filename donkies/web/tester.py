import django
import os
import sys

from os.path import abspath, dirname, join
from django.apps import apps

path = abspath(join(dirname(abspath(__file__)), '..'))
sys.path.append(path)
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE', 'donkies.settings.development')
django.setup()


class Tester:
    def send_email(self):
        from web.tasks import send_email
        send_email()

    def get_users(self):
        """
        Returns all Atrium users.
        """
        from finance.services.atrium_api import AtriumApi

        a = AtriumApi()
        return a.get_users()

    def get_lost_users(self):
        """
        Returns users that exist in Atrium and doesn't exist
        in database.
        """
        User = apps.get_model('web', 'User')

        qs = User.objects.filter(is_admin=False).values_list('guid', flat=True)
        guids = list(qs)
        guids = [guid for guid in guids if guid is not None]

        return [d for d in self.get_users() if d.guid not in guids]

    def print_users(self):
        for d in self.get_users():
            print(d)

    def print_lost_users(self):
        l = self.get_lost_users()
        if not l:
            print('No lost users')
            return

        for d in l:
            print(d)

    def get_members(self, user_id):
        """
        Returns all Atrium members for particular user.
        """
        from finance.services.atrium_api import AtriumApi
        User = apps.get_model('web', 'User')
        user = User.objects.get(id=user_id)
        a = AtriumApi()
        return a.get_members(user.guid)

    def get_lost_members(self, user_id):
        """
        Returns all members that exist in Atrium and doesn't exist in
        database.
        """
        Member = apps.get_model('finance', 'Member')
        qs = Member.objects.filter(
            user_id=user_id).values_list('guid', flat=True)
        guids = list(qs)
        qs = Member.objects.filter(user_id=user_id)
        return [d for d in self.get_members(user_id) if d.guid not in guids]

    def print_members(self):
        """
        Prints Atrium members for all users.
        """
        User = apps.get_model('web', 'User')
        for user in User.objects.filter(is_admin=False):
            print('\n------- User: {}'.format(user.email))
            for d in self.get_members(user.id):
                print(d)

    def print_lost_members(self):
        """
        Prints lost members for all users.
        """
        User = apps.get_model('web', 'User')
        for user in User.objects.filter(is_admin=False):
            print('\n------- User: {}'.format(user.email))
            for d in self.get_lost_members(user.id):
                print(d)

    def resume_halted(self):
        from finance.services.atrium_api import AtriumApi
        Member = apps.get_model('finance', 'Member')

        a = AtriumApi()
        for user in a.get_users():
            for member in Member.objects.get_atrium_members(user.guid):
                print(member.status, member.name)
                if member.status == Member.HALTED:
                    a.aggregate_member(member.user_guid, member.guid)

    def get_transactions(self, user_id):
        User = apps.get_model('web', 'User')
        Transaction = apps.get_model('finance', 'Transaction')

        user = User.objects.get(id=user_id)
        return Transaction.objects.get_atrium_transactions(user.guid)


if __name__ == '__main__':
    t = Tester()

    # from finance.services.atrium_api import AtriumApi
    # a = AtriumApi()

    # for user in t.get_users():
    #     a.delete_user(user.guid)
    #     print(user)

    # for tr in t.get_transactions(5):
    #     print(tr['date'])
