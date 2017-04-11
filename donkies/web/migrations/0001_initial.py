# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-04-11 15:06
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('encrypted_id', models.CharField(default='', max_length=32)),
                ('guid', models.CharField(blank=True, default=None, max_length=100, null=True, unique=True)),
                ('email', models.EmailField(default=None, max_length=255, null=True, unique=True)),
                ('first_name', models.CharField(blank=True, default='', max_length=50)),
                ('last_name', models.CharField(blank=True, default='', max_length=50)),
                ('address1', models.CharField(default=None, max_length=50, null=True)),
                ('address2', models.CharField(blank=True, default=None, max_length=50, null=True)),
                ('city', models.CharField(default=None, max_length=100, null=True)),
                ('state', models.CharField(choices=[('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'), ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'), ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'), ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'), ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming')], default=None, max_length=2, null=True)),
                ('postal_code', models.CharField(default=None, max_length=5, null=True, validators=[django.core.validators.RegexValidator(message='Should be 5 digits', regex='^\\d{5}$')])),
                ('date_of_birth', models.DateField(default=None, help_text='YYYY-MM-DD', null=True)),
                ('ssn', models.CharField(default=None, help_text='Last 4 digits', max_length=11, null=True, validators=[django.core.validators.RegexValidator(message='Should be XXX-XX-XXXX', regex='^\\d{3}\\-\\d{2}\\-\\d{4}$')])),
                ('phone', models.CharField(default=None, max_length=10, null=True, validators=[django.core.validators.RegexValidator(message='Should be 10 digits', regex='^\\d{10}$')])),
                ('confirmation_token', models.CharField(blank=True, max_length=255)),
                ('confirmed_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('confirmation_resend_count', models.IntegerField(default=0)),
                ('reset_token', models.CharField(max_length=255)),
                ('reset_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('last_access_date', models.DateTimeField(auto_now_add=True)),
                ('new_email', models.EmailField(default=None, max_length=255, null=True)),
                ('new_email_token', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('new_email_expire_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('profile_image', models.ImageField(blank=True, max_length=255, upload_to='user/profile_image/%Y', verbose_name='profile image')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('is_admin', models.BooleanField(default=False, verbose_name='admin')),
                ('is_superuser', models.BooleanField(default=False, verbose_name='superuser')),
                ('fb_id', models.CharField(blank=True, default=None, max_length=100, null=True, unique=True)),
                ('fb_token', models.CharField(blank=True, default='', max_length=3000)),
                ('fb_link', models.CharField(blank=True, default='', max_length=1000)),
                ('fb_name', models.CharField(blank=True, default='', max_length=255)),
                ('fb_first_name', models.CharField(blank=True, default='', max_length=255)),
                ('fb_last_name', models.CharField(blank=True, default='', max_length=255)),
                ('fb_gender', models.CharField(blank=True, default='', max_length=50)),
                ('fb_locale', models.CharField(blank=True, default='', max_length=10)),
                ('fb_age_range', models.IntegerField(default=0)),
                ('fb_timezone', models.IntegerField(default=0)),
                ('fb_verified', models.BooleanField(default=False)),
                ('minimum_transfer_amount', models.IntegerField(choices=[(5, 5), (10, 10), (20, 20), (50, 50), (100, 100)], default=5, help_text='Minimum amount for transfer.')),
                ('is_auto_transfer', models.BooleanField(default=True, help_text='Auto transfer when reach minimum amount')),
                ('is_even_roundup', models.BooleanField(default=False, help_text='Roundup even amounts $1.00, $2.00 etc')),
                ('is_signup_completed', models.BooleanField(default=False)),
                ('is_closed_account', models.BooleanField(default=False, help_text='User closed account in Donkies')),
            ],
            options={
                'verbose_name_plural': 'Users',
                'ordering': ['email'],
            },
        ),
        migrations.CreateModel(
            name='ChangeEmailHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_old', models.CharField(max_length=255)),
                ('email_new', models.CharField(max_length=255)),
                ('dt', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'change email history',
                'verbose_name_plural': 'change email history',
                'ordering': ['-dt'],
            },
        ),
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(choices=[('change_email', 'change email'), ('resend_reg_confirmation', 'resend registration confirmation'), ('reset_password', 'reset password'), ('signup', 'signup')], max_length=50)),
                ('name', models.CharField(max_length=255)),
                ('subject', models.CharField(max_length=255)),
                ('txt', models.TextField(blank=True, default='')),
                ('html', models.TextField(blank=True, default='')),
            ],
            options={
                'verbose_name': 'email',
                'verbose_name_plural': 'emails',
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='Emailer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_to', models.EmailField(max_length=100)),
                ('email_from', models.EmailField(max_length=100)),
                ('subject', models.CharField(max_length=255)),
                ('txt', models.TextField()),
                ('html', models.TextField()),
                ('report', models.TextField(default='')),
                ('sent', models.BooleanField(default=False)),
                ('result', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'email report',
                'verbose_name_plural': 'email reports',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Logging',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('http_code', models.CharField(default='', max_length=10)),
                ('level', models.CharField(default='', max_length=8)),
                ('logger_name', models.CharField(default='', max_length=20)),
                ('module', models.CharField(default='', max_length=100)),
                ('thread', models.CharField(default='', max_length=50)),
                ('thread_name', models.CharField(default='', max_length=100)),
                ('exc_info', models.CharField(default='', max_length=255)),
                ('stack_info', models.TextField(default='')),
                ('message', models.TextField(default='')),
                ('dt', models.DateTimeField(auto_now_add=True, verbose_name='date')),
            ],
            options={
                'verbose_name': 'logging',
                'verbose_name_plural': 'logging',
                'ordering': ['-dt'],
            },
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50)),
                ('value', models.CharField(blank=True, default='', max_length=255)),
                ('info', models.CharField(blank=True, default='', max_length=255)),
                ('type', models.SmallIntegerField(blank=True, choices=[(1, 'str'), (2, 'int')], default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expire_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'token',
                'verbose_name_plural': 'tokens',
                'ordering': ['-created_at'],
            },
        ),
    ]
