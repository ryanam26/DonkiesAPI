# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-03-13 08:48
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
                ('is_active', models.BooleanField(default=True, editable=False)),
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
                ('type_ds', models.CharField(choices=[('debit', 'debit'), ('debt', 'debt'), ('investment', 'investment'), ('other', 'other')], default='other', help_text='Internal type', max_length=15)),
                ('updated_at', models.DateTimeField(default=None, null=True)),
                ('transfer_share', models.IntegerField(default=0, help_text='For debt accounts in percentage. Share of transfer amount between debt accounts.The total share of all accounts should be 100%.')),
                ('is_funding_source_for_transfer', models.BooleanField(default=False, help_text='For debit account. Funding source for transfer.')),
            ],
            options={
                'verbose_name_plural': 'accounts',
                'ordering': ['type_ds', 'member'],
                'verbose_name': 'account',
            },
        ),
        migrations.CreateModel(
            name='Challenge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guid', models.CharField(max_length=100, unique=True)),
                ('field_name', models.CharField(default=None, max_length=255, null=True)),
                ('label', models.CharField(max_length=255)),
                ('type', models.CharField(max_length=255)),
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
                ('small_logo_url', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('medium_logo_url', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('sort', models.IntegerField(default=0)),
                ('is_update', models.BooleanField(default=True, help_text='Update credentials of the institution on scheduled task')),
                ('last_update', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'institutions',
                'ordering': ['sort', 'name'],
                'verbose_name': 'institution',
            },
        ),
        migrations.CreateModel(
            name='LinkDebt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('share', models.IntegerField(default=0)),
                ('account', models.ForeignKey(help_text='Debt account', on_delete=django.db.models.deletion.CASCADE, to='finance.Account')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'link debts',
                'ordering': ['user'],
                'verbose_name': 'link debt',
            },
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, editable=False)),
                ('guid', models.CharField(max_length=100, unique=True)),
                ('identifier', models.CharField(default=None, max_length=50, null=True, unique=True)),
                ('name', models.CharField(blank=True, default=None, max_length=50, null=True)),
                ('status', models.CharField(choices=[('INITIATED', 'initiated'), ('REQUESTED', 'requested'), ('CHALLENGED', 'challenged'), ('RECEIVED', 'received'), ('TRANSFERRED', 'transferred'), ('PROCESSED', 'processed'), ('COMPLETED', 'completed'), ('PREVENTED', 'prevented'), ('DENIED', 'denied'), ('HALTED', 'halted')], default='INITIATED', max_length=50)),
                ('aggregated_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('successfully_aggregated_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('metadata', django.contrib.postgres.fields.jsonb.JSONField(default=None, null=True)),
                ('is_created', models.BooleanField(default=False)),
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
            name='Stat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name_plural': 'stat',
                'ordering': ['id'],
                'verbose_name': 'stat',
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, editable=False)),
                ('guid', models.CharField(max_length=100, unique=True)),
                ('uid', models.CharField(max_length=50, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, default=None, max_digits=10, null=True)),
                ('check_number', models.IntegerField(default=None, null=True)),
                ('check_number_string', models.CharField(blank=True, default=None, max_length=255, null=True)),
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
                ('roundup', models.DecimalField(decimal_places=2, default=None, help_text='Internal field. "Change" amount.', max_digits=5, null=True)),
                ('is_processed', models.NullBooleanField(default=False, help_text='Internal flag. Roundup has been transferred')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='finance.Account')),
            ],
            options={
                'verbose_name_plural': 'transactions',
                'ordering': ['account', '-transacted_at'],
                'verbose_name': 'transaction',
            },
        ),
        migrations.CreateModel(
            name='TransferDebt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('share', models.IntegerField(help_text='Current share on processing date.')),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('processed_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('is_processed', models.BooleanField(default=False)),
                ('account', models.ForeignKey(help_text='Debt account.', on_delete=django.db.models.deletion.CASCADE, related_name='transfers_user', to='finance.Account')),
            ],
            options={
                'verbose_name_plural': 'transfers debt',
                'ordering': ['-processed_at'],
                'verbose_name': 'transfer debt',
            },
        ),
        migrations.CreateModel(
            name='TransferDonkies',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dwolla_id', models.CharField(blank=True, default=None, max_length=50, null=True, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('status', models.CharField(choices=[('pending', 'pending'), ('processed', 'processed'), ('cancelled', 'cancelled'), ('failed', 'failed'), ('reclaimed', 'reclaimed')], default=None, max_length=9, null=True)),
                ('created_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('initiated_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('updated_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('failure_code', models.CharField(blank=True, default=None, max_length=4, null=True)),
                ('is_initiated', models.BooleanField(default=False, help_text='Transfer initiated in Dwolla')),
                ('is_failed', models.BooleanField(default=False)),
                ('sent_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('processed_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('is_sent', models.BooleanField(default=False, help_text='Money sent to Donkies LLC')),
                ('is_processed_to_user', models.BooleanField(default=False, help_text='Funds processed to TransferUser model.')),
                ('account', models.ForeignKey(help_text='Funding source user debit account.', on_delete=django.db.models.deletion.CASCADE, related_name='transfers_donkies', to='finance.Account')),
            ],
            options={
                'verbose_name_plural': 'transfers donkies',
                'ordering': ['-updated_at'],
                'verbose_name': 'transfer donkies',
            },
        ),
        migrations.CreateModel(
            name='TransferDonkiesFailed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dwolla_id', models.CharField(blank=True, default=None, max_length=50, null=True, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('status', models.CharField(choices=[('pending', 'pending'), ('processed', 'processed'), ('cancelled', 'cancelled'), ('failed', 'failed'), ('reclaimed', 'reclaimed')], default=None, max_length=9, null=True)),
                ('created_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('initiated_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('updated_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('failure_code', models.CharField(blank=True, default=None, max_length=4, null=True)),
                ('is_initiated', models.BooleanField(default=False, help_text='Transfer initiated in Dwolla')),
                ('is_failed', models.BooleanField(default=False)),
                ('account', models.ForeignKey(help_text='Funding source user debit account.', on_delete=django.db.models.deletion.CASCADE, to='finance.Account')),
            ],
            options={
                'verbose_name_plural': 'transfers donkies failed',
                'ordering': ['-created_at'],
                'verbose_name': 'transfer donkies failed',
            },
        ),
        migrations.CreateModel(
            name='TransferPrepare',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('roundup', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('processed_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('is_processed', models.BooleanField(default=False)),
                ('account', models.ForeignKey(help_text='Debit account.', on_delete=django.db.models.deletion.CASCADE, related_name='transfers_prepare', to='finance.Account')),
            ],
            options={
                'verbose_name_plural': 'transfers prepare',
                'ordering': ['-created_at'],
                'verbose_name': 'transfer prepare',
            },
        ),
        migrations.CreateModel(
            name='TransferPrepareDate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'transfers prepare date',
                'ordering': ['-date'],
                'verbose_name': 'transfer prepare data',
            },
        ),
        migrations.CreateModel(
            name='TransferUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cached_amount', models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=10, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('items', models.ManyToManyField(to='finance.TransferDonkies')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'transfers user',
                'ordering': ['-created_at'],
                'verbose_name': 'transfer user',
            },
        ),
        migrations.AddField(
            model_name='transferdebt',
            name='tu',
            field=models.ForeignKey(help_text='TransferUser transfer', on_delete=django.db.models.deletion.CASCADE, to='finance.TransferUser'),
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
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to='finance.Member'),
        ),
        migrations.AlterUniqueTogether(
            name='member',
            unique_together=set([('user', 'institution')]),
        ),
        migrations.AlterUniqueTogether(
            name='linkdebt',
            unique_together=set([('user', 'account')]),
        ),
    ]
