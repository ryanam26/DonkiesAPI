from atrium import Api
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.postgres.fields import JSONField
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _

api = Api(key="bc60009946a40054ebe5bd5f5135d3566948fe08", client_id="cf67b05d-586b-44e3-a05b-175c8fd33779")


class DonkiesUserManager(BaseUserManager):

    def _create_user(self, email, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True,
                                 **extra_fields)


class DonkiesUser(AbstractBaseUser, PermissionsMixin):
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

    USERNAME_FIELD = 'email'
    objects = DonkiesUserManager()
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

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

    def connect_bank_accounts(backend, response, user=None, *args, **kwargs):
        print(user, user.fb_id, sep='\n')

        # Create a user
        user = api.createUser(payload={
            "identifier": str(user.fb_id),
            "metadata": {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email
            }
        })

        # Find the institution the user banks at.
        query = api.getInstitutions(queryParams={
            "name": "Wells Fargo"
        })
        institution = query['institutions'][0]
        creds = api.getCredentials(institution['guid'])

        # Create a member between a banking institution and the user
        member = api.createMember(user['guid'], payload={
            "institution_code": institution['code'],
            "credentials": [
                {
                    "credential_guid": creds[0]['guid'],
                    "value": "AwesomeBankUserName"
                },
                {
                    "credential_guid": creds[1]['guid'],
                    "value": "AwesomeBankPassword"
                }
            ]
        })

        # Once member is created, check status to see if all data has been obtained
        status = api.getMemberStatus(user['guid'], member['guid'])
