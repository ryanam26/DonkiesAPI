from django.db.models.signals import pre_save
from django.dispatch import receiver
from atrium import Api

from donkiesapp.models import LinkedBankAccount

api = Api(key="bc60009946a40054ebe5bd5f5135d3566948fe08", client_id="cf67b05d-586b-44e3-a05b-175c8fd33779")

# Override default endpoint with development endpoint
api.root = 'https://vestibule.mx.com/'


@receiver(pre_save, model=LinkedBankAccount)
def connect_bank_accounts(sender, instance, *args, **kwargs):
    print(sender, instance, *args, **kwargs)
    print(user, user.fb_id, sep='\n')

