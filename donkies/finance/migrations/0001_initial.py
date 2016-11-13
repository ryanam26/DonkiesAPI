# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-13 13:38
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guid', models.CharField(max_length=100, unique=True)),
                ('uid', models.CharField(max_length=50, unique=True)),
                ('name', models.CharField(default=None, max_length=255, null=True)),
                ('apr', models.DecimalField(decimal_places=6, default=None, help_text='Annual Percentage Rate.', max_digits=10, null=True)),
                ('apy', models.DecimalField(decimal_places=6, default=None, help_text='Annual Percentage Yield.', max_digits=10, null=True)),
                ('available_balance', models.DecimalField(decimal_places=2, default=None, help_text='The current available account balance.', max_digits=14, null=True)),
                ('available_credit', models.DecimalField(decimal_places=2, default=None, help_text='The current available credit balance of the account.', max_digits=10, null=True)),
                ('balance', models.DecimalField(decimal_places=2, default=None, help_text='The current Account Balance.', max_digits=14, null=True)),
                ('created_at', models.DateTimeField(default=None, null=True)),
                ('day_payment_is_due', models.IntegerField(default=None, null=True)),
                ('is_closed', models.BooleanField(default=False)),
                ('credit_limit', models.DecimalField(decimal_places=2, default=None, help_text='The credit limit for the account.', max_digits=10, null=True)),
                ('interest_rate', models.DecimalField(decimal_places=6, default=None, help_text='Interest rate, %', max_digits=10, null=True)),
                ('last_payment', models.DecimalField(decimal_places=2, default=None, help_text="Amount of the account's last payment.", max_digits=10, null=True)),
                ('last_payment_at', models.DateTimeField(default=None, null=True)),
                ('matures_on', models.DateTimeField(default=None, null=True)),
                ('minimum_balance', models.DecimalField(decimal_places=2, default=None, help_text='Minimum required balance.', max_digits=14, null=True)),
                ('minimum_payment', models.DecimalField(decimal_places=2, default=None, help_text='Minimum payment.', max_digits=10, null=True)),
                ('original_balance', models.DecimalField(decimal_places=2, default=None, help_text='Original balance.', max_digits=14, null=True)),
                ('payment_due_at', models.DateTimeField(default=None, null=True)),
                ('payoff_balance', models.DecimalField(decimal_places=2, default=None, help_text='Payoff Balance', max_digits=14, null=True)),
                ('started_on', models.DateTimeField(default=None, null=True)),
                ('subtype', models.CharField(default=None, max_length=255, null=True)),
                ('total_account_value', models.DecimalField(decimal_places=2, default=None, help_text='The total value of the account.', max_digits=14, null=True)),
                ('type', models.CharField(default=None, max_length=100, null=True)),
                ('updated_at', models.DateTimeField(default=None, null=True)),
            ],
            options={
                'verbose_name_plural': 'accounts',
                'ordering': ['member'],
                'verbose_name': 'account',
            },
        ),
        migrations.CreateModel(
            name='Challenge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guid', models.CharField(max_length=100, unique=True)),
                ('field_name', models.CharField(max_length=255)),
                ('label', models.CharField(max_length=255)),
                ('type', models.CharField(max_length=255)),
                ('value', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('is_responded', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'challenges',
                'ordering': ['member'],
                'verbose_name': 'challenge',
            },
        ),
        migrations.CreateModel(
            name='Credentials',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guid', models.CharField(max_length=100, unique=True)),
                ('field_name', models.CharField(max_length=255)),
                ('label', models.CharField(max_length=255)),
                ('type', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name_plural': 'credentials',
                'ordering': ['institution'],
                'verbose_name': 'credentials',
            },
        ),
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=100, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('url', models.CharField(max_length=255)),
                ('sort', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name_plural': 'institutions',
                'ordering': ['sort', 'name'],
                'verbose_name': 'institution',
            },
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guid', models.CharField(max_length=100, unique=True)),
                ('identifier', models.CharField(default=None, max_length=50, null=True, unique=True)),
                ('name', models.CharField(blank=True, default=None, max_length=50, null=True)),
                ('status', models.CharField(choices=[('INITIATED', 'initiated'), ('REQUESTED', 'requested'), ('CHALLENGED', 'challenged'), ('RECEIVED', 'received'), ('TRANSFERRED', 'transferred'), ('PROCESSED', 'processed'), ('COMPLETED', 'completed'), ('PREVENTED', 'prevented'), ('DENIED', 'denied'), ('HALTED', 'halted')], default='INITIATED', max_length=50)),
                ('aggregated_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('successfully_aggregated_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('metadata', django.contrib.postgres.fields.jsonb.JSONField(default=None, null=True)),
                ('institution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.Institution')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'members',
                'ordering': ['user'],
                'verbose_name': 'member',
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guid', models.CharField(max_length=100, unique=True)),
                ('uid', models.CharField(max_length=50, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, default=None, max_digits=5, null=True)),
                ('check_number', models.IntegerField(default=None, null=True)),
                ('category', models.CharField(default=None, max_length=255, null=True)),
                ('created_at', models.DateTimeField(default=None, null=True)),
                ('date', models.DateField(default=None, null=True)),
                ('description', models.CharField(default=None, max_length=3000, null=True)),
                ('is_bill_pay', models.NullBooleanField()),
                ('is_direct_deposit', models.NullBooleanField()),
                ('is_expense', models.NullBooleanField()),
                ('is_fee', models.NullBooleanField()),
                ('is_income', models.NullBooleanField()),
                ('is_overdraft_fee', models.NullBooleanField()),
                ('is_payroll_advance', models.NullBooleanField()),
                ('latitude', models.DecimalField(decimal_places=6, default=None, max_digits=10, null=True)),
                ('longitude', models.DecimalField(decimal_places=6, default=None, max_digits=10, null=True)),
                ('memo', models.CharField(default=None, max_length=255, null=True)),
                ('merchant_category_code', models.IntegerField(default=None, null=True)),
                ('original_description', models.CharField(default=None, max_length=3000, null=True)),
                ('posted_at', models.DateTimeField(default=None, null=True)),
                ('status', models.CharField(max_length=50)),
                ('top_level_category', models.CharField(default=None, max_length=255, null=True)),
                ('transacted_at', models.DateTimeField(default=None, null=True)),
                ('type', models.CharField(max_length=50)),
                ('updated_at', models.DateTimeField(default=None, null=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.Account')),
            ],
            options={
                'verbose_name_plural': 'transactions',
                'ordering': ['account'],
                'verbose_name': 'transaction',
            },
        ),
        migrations.AddField(
            model_name='credentials',
            name='institution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.Institution'),
        ),
        migrations.AddField(
            model_name='challenge',
            name='member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.Member'),
        ),
        migrations.AddField(
            model_name='account',
            name='member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.Member'),
        ),
        migrations.AlterUniqueTogether(
            name='member',
            unique_together=set([('user', 'institution')]),
        ),
    ]
