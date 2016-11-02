from django.db import models
from donkiesoauth2.models import DonkiesUser


class LinkedBankAccount(models.Model):
    user = models.ForeignKey(DonkiesUser)
    guid = models.CharField(max_length=250, null=True)

