"""
Signup flow.
After signup user need to go through following steps:

For Dwolla:

1) Complete profile
2) Add debit bank to Plaid
3) Add debit bank to Dwolla (IAV)
4) Add debt to Plaid

For Stripe:
2) Add debit bank to Plaid
4) Add debt to Plaid
"""

import datetime
import json
import requests
import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.apps import apps
from django.conf import settings
from django.db.models import Sum
from django.core.validators import RegexValidator
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from web.services.helpers import get_md5


class UserManager(BaseUserManager):
    def create_user(self, email, password, guid=None):
        if not email:
            raise ValueError('Please input email.')
        user = self.model(email=email)
        user.set_password(password)

        if guid is not None:
            user.guid = guid

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


class User(AbstractBaseUser):
    TRANSFER_AMOUNT_CHOICES = (
        (5, 5),
        (10, 10),
        (20, 20),
        (50, 50),
        (100, 100)
    )

    encrypted_id = models.CharField(max_length=32, default='')
    guid = models.CharField(
        max_length=100,
        null=True,
        default=None,
        blank=True,
        unique=True)
    email = models.EmailField(
        max_length=255, null=True, unique=True, default=None)
    first_name = models.CharField(max_length=50, blank=True, default='')
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
        default=None
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
    minimum_transfer_amount = models.IntegerField(
        choices=TRANSFER_AMOUNT_CHOICES,
        default=TRANSFER_AMOUNT_CHOICES[0][0],
        help_text='Minimum amount for transfer.')
    is_auto_transfer = models.BooleanField(
        default=True, help_text='Auto transfer when reach minimum amount')
    is_even_roundup = models.BooleanField(
        default=False, help_text='Roundup even amounts $1.00, $2.00 etc')
    is_signup_completed = models.BooleanField(default=False)
    is_closed_account = models.BooleanField(
        default=False, help_text='User closed account in Donkies')

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

    @property
    def is_profile_completed(self):
        """
        Profile completed. After profile has been completed,
        user can not it change.
        """
        fields = (
            'first_name',
            'last_name',
            'address1',
            'city',
            'state',
            'postal_code',
            'date_of_birth',
            'ssn',
            'phone'
        )
        for field in fields:
            if getattr(self, field) is None:
                return False
        return True

    @property
    def total_debt(self):
        """
        Returns user's total debt.
        Make sense only with Plaid debt accounts.
        Doesn't make sense with manual accounts as we do
        not know balance.
        """
        return 0
        Account = apps.get_model('finance', 'Account')
        res = Account.objects.debt_accounts().filter(
            item__user=self).aggregate(Sum('balance'))
        debt = res['balance__sum']
        if debt is None:
            return 0
        return debt

    def check_signup_step1(self):
        """
        Entire user profile should be filled.
        """
        return self.is_profile_completed

    def check_signup_step2(self):
        """
        User should add debit account to Atrium.
        """
        Account = apps.get_model('finance', 'Account')
        count = Account.objects.debit_accounts().filter(
            item__user=self).count()
        if count > 0:
            return True
        return False

    def check_signup_step3(self):
        """
        User should add debit account to Dwolla.
        """
        return True
        if self.get_funding_source_account() is None:
            return False
        return True

    def check_signup_step4(self):
        """
        User should add debt account to Plaid.
        """
        Account = apps.get_model('finance', 'Account')
        count = Account.objects.debt_accounts().filter(
            item__user=self).count()
        if count > 0:
            return True
        return False

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
        link = '{url}/confirm?id={id}&token={token}'
        return link.format(**dic)

    def get_reset_link(self):
        dic = dict(
            url=settings.FRONTEND_URL,
            id=self.encrypted_id,
            token=self.reset_token
        )
        link = '{url}/reset?id={id}&token={token}'
        return link.format(**dic)

    def signup(self):
        # Emailer = apps.get_model('web', 'Emailer')
        # Email = apps.get_model('web', 'Email')
        # Emailer.objects.process_email(Email.SIGNUP, user=self)
        pass

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
        Emailer.objects.process_email(
            Email.RESEND_REG_CONFIRMATION, user=self)

    def reset_request(self):
        Emailer = apps.get_model('web', 'Emailer')
        Email = apps.get_model('web', 'Email')
        self.reset_token = self.generate_token()
        self.reset_at = timezone.now()
        self.save()
        Emailer.objects.process_email(Email.RESET_PASSWORD, user=self)

    def reset_password(self, new_password):
        """
        Sets new password and clears reset token
        """
        self.set_password(new_password)
        self.reset_token = ''
        self.reset_at = None
        self.save()

    def change_email_request(self, new_email):
        Emailer = apps.get_model('web', 'Emailer')
        Email = apps.get_model('web', 'Email')

        self.new_email = new_email
        self.new_email_token = self.generate_token()
        self.new_email_expire_at =\
            timezone.now() + datetime.timedelta(hours=1)
        self.save()
        Emailer.objects.process_email(Email.CHANGE_EMAIL, user=self)

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
        link = '{url}/change_email_confirm?id={id}&token={token}'
        return link.format(**dic)

    def get_funding_source_account(self):
        """
        Returns user's funding source debit account or None
        if user has not set funding source account yet.
        """
        Account = apps.get_model('finance', 'Account')
        return Account.objects.active().filter(
            item__user=self, is_funding_source_for_transfer=True).first()

    def get_not_processed_roundup_sum(self):
        """
        Returns total roundup of all user's accounts
        where roundup has not been processed yet.
        """
        Transaction = apps.get_model('finance', 'Transaction')
        sum = Transaction.objects.active()\
            .filter(
                account__is_active=True,
                account__item__user_id=self.id,
                is_processed=False)\
            .aggregate(Sum('roundup'))['roundup__sum']
        sum = 0 if sum is None else sum
        return sum

    @property
    def new_email_expired(self):
        if not self.new_email_expire_at:
            return True
        return timezone.now() > self.new_email_expire_at

    def save_facebook_picture(self):
        if self.fb_id is None:
            return
        url = 'https://graph.facebook.com/{}/picture'.format(self.fb_id)
        url += '?width=1200'

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

    def signup_steps(self):
        # Account = apps.get_model('finance', 'Account')
        if self.is_signup_completed:
            return None

        # url_3rd_step = None
        # if self.check_signup_step2():
        #     account = Account.objects.debit_accounts().filter(
        #         item__user=self).first()
        #     url_3rd_step = '/create_funding_source?account_guid={}'.format(
        #         account.guid)

        return [
            # {
            #     'name': 'Complete user profile',
            #     'message': 'Please complete your profile',
            #     'allowed_url': '/user_profile',
            #     'is_completed': self.check_signup_step1()
            # },
            {
                'name': 'Add debit account to Plaid.',
                'message': 'Please add debit account.',
                'allowed_url': '/add_bank',
                'is_completed': self.check_signup_step2()
            },
            # {
            #     'name': 'Add debit account to Dwolla.',
            #     'message': 'Please verify your debit account in Dwolla.',
            #     'allowed_url': url_3rd_step,
            #     'is_completed': self.check_signup_step3()
            # },
            # {
            #     'name': 'Add debt account to Atrium.',
            #     'message': 'Please add debt account.',
            #     'allowed_url': '/add_lender',
            #     'is_completed': self.check_signup_step4()
            # },
        ]

    def close_account(self):
        """
        Close account in Donkies and refund all roundup.
        1) Transfer all funds that currently Donkies hold in Stripe
           to TransferUser model.
        2) Delete all items, accounts and transactions
            (mark is_active=False)
        """
        Item = apps.get_model('finance', 'Item')
        TransferUser = apps.get_model('ach', 'TransferUser')

        TransferUser.objects.process_user(self.id, force_process=True)

        qs = Item.objects.active().filter(user=self)
        for item in qs:
            Item.objects.delete_item(item.id)

        self.is_closed_account = True
        self.save()

    def save(self, *args, **kwargs):
        Token = apps.get_model('web', 'Token')
        created = True if not self.pk else False
        super().save(*args, **kwargs)

        if created:
            self.confirmation_token = self.generate_token()
            self.encrypted_id = self.encrypt(self.id)
            self.guid = uuid.uuid4().hex
            Token.objects.create(user=self)
            self.save()

        # If user completed all signup steps - mark in db.
        if not self.is_signup_completed:
            if self.signup_steps() is not None:
                is_completed = True
                for d in self.signup_steps():
                    if d['is_completed'] is False:
                        is_completed = False
                if is_completed:
                    self.is_signup_completed = True
                    self.save()

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

        if user.fb_first_name:
            user.first_name = user.fb_first_name

        if user.fb_last_name:
            user.last_name = user.fb_last_name

        user.is_confirmed = True
        user.confirmed_at = timezone.now()
        user.save()

        # save picture
        user.save_facebook_picture()
        return user

    @staticmethod
    def get_facebook_login_url():
        url = 'https://www.facebook.com/dialog/oauth?client_id='
        url += settings.FACEBOOK_APP_ID
        url += '&redirect_uri='
        url += settings.FACEBOOK_REDIRECT_URI
        return url

    @staticmethod
    def get_admin_urls():
        return [
            (r'^custom/clean_plaid/$', 'clean_plaid'),
        ]
