from django.contrib.postgres.fields import JSONField
from django.core.mail import send_mail
from django.db import models
from django.db import transaction
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

import json
from time import sleep

from atrium import Api

api = Api(key="bc60009946a40054ebe5bd5f5135d3566948fe08", client_id="cf67b05d-586b-44e3-a05b-175c8fd33779")

# Override default endpoint with development endpoint
api.root = 'https://vestibule.mx.com/'


class DonkiesUser(models.Model):
    fb_id = models.BigIntegerField(default=0)
    email = models.EmailField(max_length=250, unique=True)
    name = models.CharField(max_length=250)
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    age_range = JSONField(null=True)
    birthday = models.DateField(null=True)
    phone_number = models.CharField(max_length=20, null=True)
    link = models.CharField(max_length=250, null=True)
    gender = models.CharField(max_length=25, null=True)
    locale = models.CharField(max_length=50, null=True)
    picture = models.ImageField(null=True)
    user_timezone = models.CharField(max_length=25, null=True)
    updated_time = models.DateTimeField(null=True)
    verified = models.CharField(max_length=25, null=True)
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    is_staff = models.BooleanField(
        _('active'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as staff. '
        ),
    )
    is_superuser = models.BooleanField(
        _('active'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as superuser. '
        ),
    )
    is_developer = models.BooleanField(
        _('developer'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as developer. '
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.email)

    def __str__(self):
        return self.email

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])


class LinkedBankAccount(models.Model):
    user = models.ForeignKey(DonkiesUser)
    user_api_id = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100)
    PROCESSING = 'PR'
    FAILED = 'FA'
    CHALLENGED = 'CH'
    COMPLETE = 'CM'
    STATUS_API_CHOICES = (
        (PROCESSING, 'Processing'),
        (FAILED, 'Failed'),
        (CHALLENGED, 'Challenged'),
        (COMPLETE, 'Complete'),
    )
    status = models.CharField(max_length=2, choices=STATUS_API_CHOICES)

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Create a user in MX
        user = api.createUser(payload={
            "identifier": str(self.user.pk),
            "metadata": json.dumps({
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "email": self.user.email
            })
        })

        # Store user GUID
        self.user_api_id = user['guid']

        # Find the institution the user banks at.
        query = api.getInstitutions(queryParams={
            "name": self.bank_name
        })
        self.bank_name_api = institution = query['institutions'][0]
        creds = api.getCredentials(institution['code'])

        # Create a member between a banking institution and the user
        member = api.createMember(user['guid'], payload={
            "institution_code": institution['code'],
            "credentials": [
                {
                    "guid": creds[0]['guid'],
                    "value": kwargs['BankUserName']
                },
                {
                    "guid": creds[1]['guid'],
                    "value": kwargs['BankPassword']
                }
            ]
        })

        # Once member is created, check status to see if all data has been obtained

        processing_statuses = ['INITIATED', 'REQUESTED', 'AUTHENTICATED', 'TRANSFERRED', 'PROCESSED', ]
        failed_statuses = ['PREVENTED', 'DENIED', 'HALTED', ]
        complete_statuses = ['COMPLETED', ]
        action_statuses = ['CHALLENGED', ]

        while api.getMemberStatus(user['guid'], member['guid'])['status'] in processing_statuses:
            self.status = 'PR'
            super(LinkedBankAccount, self).save(*args, **kwargs)
            sleep(1)

        if api.getMemberStatus(user['guid'], member['guid'])['status'] in complete_statuses:
            self.status = 'CM'

        elif api.getMemberStatus(user['guid'], member['guid'])['status'] in action_statuses:
            self.status = 'CH'

        elif api.getMemberStatus(user['guid'], member['guid'])['status'] in failed_statuses:
            self.status = 'FA'

        super(LinkedBankAccount, self).save(*args, **kwargs)


class LinkedBankAccountTransaction(models.Model):
    linked_bank_account = models.ForeignKey(LinkedBankAccount)
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.FloatField()
    EXPENSE = 'EX'
    FEE = 'FE'
    INCOME = 'IN'
    OVERDRAFT_FEE = 'OF'
    OTHER = 'OT'
    STATUS_API_CHOICES = (
        (EXPENSE, 'Expense'),
        (FEE, 'Fee'),
        (INCOME, 'Income'),
        (OVERDRAFT_FEE, 'Overdraft Fee'),
        (OTHER, 'Other')
    )
    transaction_type = models.CharField(max_length=2, choices=STATUS_API_CHOICES)
    transaction_api_details = JSONField()

