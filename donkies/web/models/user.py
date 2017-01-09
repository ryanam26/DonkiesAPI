import datetime
import json
import requests
import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.apps import apps
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
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
        user.is_confirmed = True
        user.confirmed_at = timezone.now()
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def create_atrium_user(self, user_id):
        """
        Do not create atrium user for "admin" user.
        TODO: processing errors.
        """
        User = apps.get_model('web', 'User')
        user = User.objects.get(id=user_id)
        if user.is_admin:
            return

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
    profile_image = models.ImageField(
        verbose_name='profile image',
        max_length=255,
        blank=True,
        upload_to='user/profile_image/%Y')
    is_active = models.BooleanField(default=True, verbose_name='active')
    is_admin = models.BooleanField(default=False, verbose_name='admin')
    is_superuser = models.BooleanField(default=False, verbose_name='superuser')
    fb_id = models.CharField(
        max_length=100,
        default=None,
        null=True,
        unique=True,
        blank=True)
    fb_token = models.CharField(max_length=3000, blank=True, default='')
    fb_link = models.CharField(max_length=1000, blank=True, default='')
    fb_name = models.CharField(max_length=255, blank=True, default='')
    fb_first_name = models.CharField(max_length=255, blank=True, default='')
    fb_last_name = models.CharField(max_length=255, blank=True, default='')
    fb_gender = models.CharField(max_length=50, blank=True, default='')
    fb_locale = models.CharField(max_length=10, blank=True, default='')
    fb_age_range = models.IntegerField(default=0)
    fb_timezone = models.IntegerField(default=0)
    fb_verified = models.BooleanField(default=False)
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

    def save_facebook_picture(self):
        if self.fb_id is None:
            return
        url = 'https://graph.facebook.com/{}/picture'.format(self.fb_id)
        url += '?width=320&height=320'

        try:
            r = requests.get(url)
        except:
            return

        if r.status_code != 200:
            return

        bytes = r.content
        extension = '.jpg'

        filename = uuid.uuid4().hex + extension.lower()
        self.profile_image.save(filename, ContentFile(bytes))

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

    @staticmethod
    def get_facebook_user(code, redirect_uri):
        """
        Input: facebook "code" and "redirect uri".
        Requests info from facebook.
        Returns dict with id and email or raise validation error.
        Use this method in serializer, that can process validation error.
        """
        # Step1. Get access_token
        url = 'https://graph.facebook.com/v2.8/oauth/access_token'
        url += '?client_id={}'.format(settings.FACEBOOK_APP_ID)
        url += '&redirect_uri={}'.format(redirect_uri)
        url += '&client_secret={}'.format(settings.FACEBOOK_APP_SECRET)
        url += '&code={}'.format(code)

        try:
            resp = requests.get(url)
        except requests.exceptions.ConnectionError:
            raise ValidationError('Connection error.')

        dic = json.loads(resp.text)
        if 'error' in dic:
            raise ValidationError(dic['error']['message'])

        access_token = dic['access_token']

        fields = (
            'id',
            'email',
            'name',
            'first_name',
            'last_name',
            'age_range',
            'link',
            'gender',
            'locale',
            'picture',
            'timezone',
            'updated_time',
            'verified'
        )

        url = 'https://graph.facebook.com/me?fields={}'.format(
            ','.join(fields))
        url += '&access_token={}'.format(access_token)
        try:
            resp = requests.get(url)
        except requests.exceptions.ConnectionError:
            raise ValidationError('Connection error.')

        dic = json.loads(resp.text)
        if 'error' in dic:
            raise ValidationError(dic['error']['message'])

        if 'id' not in dic:
            raise ValidationError('User id is not available.')

        # If email is not available, use <fb_id>@facebook.com as email.
        if 'email' not in dic:
            dic['email'] = '{}@facebook.com'.format(dic['id'])

        dic['access_token'] = access_token
        return dic

    @staticmethod
    def create_facebook_user(dic):
        """
        Creates user from facebook data and fills appropriate fields.
        """
        user = User.objects.create_user(dic['email'], uuid.uuid4().hex)
        user.is_email_confirmed = True

        map_fields = {
            'id': 'fb_id',
            'name': 'fb_name',
            'first_name': 'fb_first_name',
            'last_name': 'fb_last_name',
            'link': 'fb_link',
            'gender': 'fb_gender',
            'locale': 'fb_locale',
            'timezone': 'fb_timezone',
            'verified': 'fb_verified',
            'access_token': 'fb_token',
        }

        for k1, k2 in map_fields.items():
            if k1 in dic:
                setattr(user, k2, dic[k1])

        # set age_range
        if 'age_range' in dic and 'min' in dic['age_range']:
            value = dic['age_range']['min']
            if str(value).isdigit():
                user.fb_age_range = value

        user.save()

        # save picture
        user.save_facebook_picture()
        return user
