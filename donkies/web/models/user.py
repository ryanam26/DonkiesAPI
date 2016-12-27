import datetime
import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.postgres.fields import JSONField
from django.utils import timezone
from django.apps import apps
from django.conf import settings
from django.core.validators import RegexValidator
from web.services.helpers import get_md5
from finance.services.atrium_api import AtriumApi
from finance import tasks


class UserManager(BaseUserManager):
    def create_user(self, email, password):
        if not email:
            raise ValueError('Please input email.')
        user = self.model(email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password=password)
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def create_atrium_user(self, user_id):
        """
        TODO: processing errors.
        """
        User = apps.get_model('web', 'User')
        user = User.objects.get(id=user_id)

        a = AtriumApi()
        guid = a.create_user(user.identifier)
        user.guid = guid
        user.save()

    def delete_atrium_user(self, guid):
        """
        TODO: processing errors
        """
        a = AtriumApi()
        a.delete_user(guid)

    def clean_atrium(self):
        """
        Delete all users in Atrium.
        TODO: processing errors.
        """
        a = AtriumApi()
        res = a.get_users()
        for d in res['users']:
            a.delete_user(d['guid'])

    def login_facebook(self, fb_response):
        """
        Get or create user.
        Save updated response from facebook to database.
        Returns dict with "message" if error.
        Returns dict with "token" if success.
        TODO: facebook may send response with error.
              Process facebook error.
        """
        d = fb_response
        if 'id' not in d:
            return {'message': 'No id'}

        if 'email' not in d:
            return {'message': 'No email'}

        try:
            user = self.model.objects.get(fb_id=d['id'])
            user.fb_response = fb_response
            user.save()
            token = user.update_token()
        except self.model.DoesNotExist:
            user = self.model.objects.create_user(d['email'], uuid.uuid4().hex)
            user.fb_id = d['id']
            user.fb_response = fb_response
            user.save()
            token = user.get_token()
        return {'token': token.key}


class User(AbstractBaseUser):
    encrypted_id = models.CharField(max_length=32, default='')
    guid = models.CharField(
        max_length=100,
        null=True,
        default=None,
        blank=True,
        unique=True,
        help_text='Atrium guid')
    identifier = models.CharField(
        max_length=50,
        null=True,
        default=None,
        blank=True,
        help_text='Used in Atrium')
    email = models.EmailField(
        max_length=255, null=True, unique=True, default=None)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True, default='')
    address1 = models.CharField(max_length=50, null=True, default=None)
    address2 = models.CharField(
        max_length=50, null=True, default=None, blank=True)
    city = models.CharField(max_length=100, null=True, default=None)
    state = models.CharField(
        max_length=2,
        null=True,
        default=None,
        choices=settings.US_STATES)
    postal_code = models.CharField(
        max_length=5,
        null=True,
        default=None,
        validators=[
            RegexValidator(
                regex='^\d{5}$',
                message='Should be 5 digits')]
    )
    date_of_birth = models.DateField(
        null=True, default=None, help_text='YYYY-MM-DD')
    ssn = models.CharField(
        help_text='Last 4 digits',
        max_length=11,
        null=True,
        default=None,
        validators=[
            RegexValidator(
                regex='^\d{3}\-\d{2}\-\d{4}$',
                message='Should be XXX-XX-XXXX')]
    )
    phone = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex='^\d{10}$',
                message='Should be 10 digits')],
        null=True,
        default=None,
        blank=True
    )
    confirmation_token = models.CharField(max_length=255, blank=True)
    confirmed_at = models.DateTimeField(blank=True, default=None, null=True)
    confirmation_resend_count = models.IntegerField(default=0)
    reset_token = models.CharField(max_length=255)
    reset_at = models.DateTimeField(blank=True, default=None, null=True)
    is_confirmed = models.BooleanField(default=False)
    last_access_date = models.DateTimeField(auto_now_add=True)
    new_email = models.EmailField(
        max_length=255, null=True, default=None)
    new_email_token = models.CharField(
        max_length=255, null=True, default=None, blank=True)
    new_email_expire_at = models.DateTimeField(
        null=True, default=None, blank=True)
    is_active = models.BooleanField(default=True, verbose_name='active')
    is_admin = models.BooleanField(default=False, verbose_name='admin')
    is_superuser = models.BooleanField(default=False, verbose_name='superuser')
    fb_id = models.CharField(
        max_length=100, null=True, default=None, unique=True)
    fb_response = JSONField(null=True, default=None)
    is_atrium_created = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name_plural = 'Users'
        ordering = ['email']
        app_label = 'web'

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    def get_short_name(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    def encrypt(self, value):
        s = '{}-{}'.format(settings.SECRET_KEY, value)
        return get_md5(s)

    def get_token(self):
        Token = apps.get_model('web', 'Token')
        token = Token.objects.filter(
            user=self, expire_at__gt=timezone.now()).first()
        if token:
            return token
        return Token.objects.create(self)

    def update_token(self):
        now = timezone.now()
        mins = settings.TOKEN_EXPIRE_MINUTES
        t = self.get_token()
        t.expire_at = now + datetime.timedelta(minutes=mins)
        t.save()
        return t

    def generate_token(self):
        value = uuid.uuid4().hex
        return self.encrypt(value)

    def get_confirmation_link(self):
        dic = dict(
            url=settings.FRONTEND_URL,
            id=self.encrypted_id,
            token=self.confirmation_token
        )
        link = '{url}/account/confirm?id={id}&token={token}'
        return link.format(**dic)

    def get_reset_link(self):
        dic = dict(
            url=settings.FRONTEND_URL,
            id=self.encrypted_id,
            token=self.reset_token
        )
        link = '{url}/account/reset?id={id}&token={token}'
        return link.format(**dic)

    def signup(self):
        Emailer = apps.get_model('web', 'Emailer')
        Email = apps.get_model('web', 'Email')
        Emailer.objects.mail_user(self, Email.SIGNUP)

    def signup_confirm(self):
        """
        Returns site's token.
        Updates "confirmed_at" to NOW().
        """
        self.is_confirmed = True
        self.confirmed_at = timezone.now()
        self.confirmation_token = ''
        self.save()
        return self.get_token()

    def resend_confirmation_link(self):
        """
        If 5 emails for resend confirmation has been sent to user,
        it might possible, that somebody tries to abuse
        somebody other's email. Do nothing!
        """
        Emailer = apps.get_model('web', 'Emailer')
        Email = apps.get_model('web', 'Email')
        if self.confirmation_resend_count >= 5:
            return

        self.confirmation_resend_count += 1
        self.save()
        Emailer.objects.mail_user(self, Email.RESEND_REG_CONFIRMATION)

    def reset_require(self):
        Emailer = apps.get_model('web', 'Emailer')
        Email = apps.get_model('web', 'Email')
        self.reset_token = self.generate_token()
        self.reset_at = timezone.now()
        self.save()
        Emailer.objects.mail_user(self, Email.RESET_PASSWORD)

    def reset_password(self, new_password):
        """
        Sets new password and clears reset token
        """
        self.set_password(new_password)
        self.reset_token = ''
        self.save()

    def change_email_request(self, new_email):
        Emailer = apps.get_model('web', 'Emailer')
        Email = apps.get_model('web', 'Email')

        self.new_email = new_email
        self.new_email_token = self.generate_token()
        self.new_email_expire_at =\
            timezone.now() + datetime.timedelta(hours=1)
        self.save()
        Emailer.objects.mail_user(self, Email.CHANGE_EMAIL)

    def change_email_confirm(self, token):
        """
        Returns bool.
        """
        ChangeEmailHistory = apps.get_model('web', 'ChangeEmailHistory')

        if self.new_email_token != token:
            return False

        if timezone.now() > self.new_email_expire_at:
            return False

        # history
        d = {
            'user': self,
            'email_old': self.email,
            'email_new': self.new_email,
        }
        ChangeEmailHistory.objects.create(**d)

        self.email = self.new_email
        self.new_email = None
        self.new_email_token = None
        self.new_email_expire_at = None
        self.save()
        return True

    def get_change_email_link(self):
        dic = dict(
            url=settings.FRONTEND_URL,
            id=self.encrypted_id,
            token=self.new_email_token
        )
        link = '{url}/account/change_email_confirm?id={id}&token={token}'
        return link.format(**dic)

    @property
    def new_email_expired(self):
        if not self.new_email_expire_at:
            return True
        return timezone.now() > self.new_email_expire_at

    def save(self, *args, **kwargs):
        Token = apps.get_model('web', 'Token')
        created = True if not self.pk else False
        if self.guid:
            self.is_atrium_created = True
        super().save(*args, **kwargs)

        if created:
            self.confirmation_token = self.generate_token()
            self.encrypted_id = self.encrypt(self.id)
            self.identifier = uuid.uuid4().hex
            Token.objects.create(user=self)
            self.save()

            # Create atrium user in background
            tasks.create_atrium_user.delay(self.id)
