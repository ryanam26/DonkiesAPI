# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-09 22:52
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


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
                ('type_ds', models.CharField(choices=[('debit', 'debit'), ('dept', 'debt'), ('investment', 'investment'), ('other', 'other')], default='other', help_text='Internal type', max_length=15)),
                ('updated_at', models.DateTimeField(default=None, null=True)),
            ],
            options={
                'verbose_name': 'account',
                'ordering': ['member'],
                'verbose_name_plural': 'accounts',
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
                'verbose_name': 'challenge',
                'ordering': ['member'],
                'verbose_name_plural': 'challenges',
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
                'verbose_name': 'credentials',
                'ordering': ['institution'],
                'verbose_name_plural': 'credentials',
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
                ('is_update', models.BooleanField(default=True, help_text='Update credentials of the institution on scheduled task')),
                ('last_update', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'institution',
                'ordering': ['sort', 'name'],
                'verbose_name_plural': 'institutions',
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
                'verbose_name': 'link debt',
                'ordering': ['user'],
                'verbose_name_plural': 'link debts',
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
                ('is_created', models.BooleanField(default=False)),
                ('institution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.Institution')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'member',
                'ordering': ['user'],
                'verbose_name_plural': 'members',
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
                ('is_processed', models.BooleanField(default=False, help_text='Internal flag. Change has been transferred to debt account')),
                ('latitude', models.DecimalField(decimal_places=6, default=None, max_digits=10, null=True)),
                ('longitude', models.DecimalField(decimal_places=6, default=None, max_digits=10, null=True)),
                ('memo', models.CharField(default=None, max_length=255, null=True)),
                ('merchant_category_code', models.IntegerField(default=None, null=True)),
                ('original_description', models.CharField(default=None, max_length=3000, null=True)),
                ('posted_at', models.DateTimeField(default=None, null=True)),
                ('roundup', models.DecimalField(decimal_places=2, default=None, help_text='Internal field. "Change" amount.', max_digits=5, null=True)),
                ('status', models.CharField(max_length=50)),
                ('top_level_category', models.CharField(default=None, max_length=255, null=True)),
                ('transacted_at', models.DateTimeField(default=None, null=True)),
                ('type', models.CharField(max_length=50)),
                ('updated_at', models.DateTimeField(default=None, null=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.Account')),
            ],
            options={
                'verbose_name': 'transaction',
                'ordering': ['account'],
                'verbose_name_plural': 'transactions',
            },
        ),
        migrations.CreateModel(
            name='Transfer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('dt', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_processed', models.BooleanField(default=False)),
                ('account_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfers_from', to='finance.Account')),
                ('account_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfers_to', to='finance.Account')),
            ],
            options={
                'verbose_name': 'transfer',
                'ordering': ['dt'],
                'verbose_name_plural': 'transfers',
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
        migrations.AlterUniqueTogether(
            name='linkdebt',
            unique_together=set([('user', 'account')]),
        ),
    ]
