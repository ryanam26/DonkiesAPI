# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-04-11 22:30
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
                ('plaid_id', models.CharField(blank=True, default=None, help_text='None for manual accounts.', max_length=255, null=True)),
                ('name', models.CharField(help_text='Set by user or institution', max_length=255)),
                ('official_name', models.CharField(blank=True, default=None, help_text='The official name given by the financial institution.', max_length=255, null=True)),
                ('balance', models.IntegerField(blank=True, default=None, null=True)),
                ('balances', django.contrib.postgres.fields.jsonb.JSONField(default=None, null=True)),
                ('mask', models.CharField(blank=True, default=None, help_text='Last 4 digits of account number', max_length=4, null=True)),
                ('subtype', models.CharField(choices=[('depository', 'depository'), ('credit', 'credit'), ('loan', 'loan'), ('mortgage', 'mortgage'), ('brokerage', 'brokerage'), ('other', 'other')], default=None, max_length=255, null=True)),
                ('type', models.CharField(choices=[('depository', 'depository'), ('credit', 'credit'), ('loan', 'loan'), ('mortgage', 'mortgage'), ('brokerage', 'brokerage'), ('other', 'other')], default=None, max_length=100, null=True)),
                ('type_ds', models.CharField(choices=[('debit', 'debit'), ('debt', 'debt'), ('other', 'other')], default='other', help_text='Internal type', max_length=15)),
                ('transfer_share', models.IntegerField(default=0, help_text='For debt accounts in percentage. Share of transfer amount between debt accounts.The total share of all accounts should be 100%.')),
                ('is_funding_source_for_transfer', models.BooleanField(default=False, help_text='For debit account. Funding source for transfer.')),
                ('account_number', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('routing_number', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('wire_routing', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('additional_info', models.CharField(blank=True, default=None, help_text='Used for manual debt accounts.', max_length=500, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(default=None, null=True)),
            ],
            options={
                'verbose_name_plural': 'accounts',
                'verbose_name': 'account',
                'ordering': ['type_ds', 'item', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plaid_id', models.CharField(max_length=50)),
                ('group', models.CharField(max_length=50)),
                ('hierarchy', django.contrib.postgres.fields.jsonb.JSONField()),
            ],
            options={
                'verbose_name_plural': 'categories',
                'verbose_name': 'category',
                'ordering': ['plaid_id'],
            },
        ),
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plaid_id', models.CharField(default=None, help_text='None for manual institutions.', max_length=100, null=True, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('has_mfa', models.BooleanField(default=False)),
                ('mfa', django.contrib.postgres.fields.jsonb.JSONField(default=None, null=True)),
                ('credentials', django.contrib.postgres.fields.jsonb.JSONField(default=None, null=True)),
                ('products', django.contrib.postgres.fields.jsonb.JSONField(default=None, null=True)),
                ('address', models.CharField(blank=True, default=None, help_text='Used for manual institutions.', max_length=500, null=True)),
                ('is_manual', models.BooleanField(default=False, help_text='Used for debt accounts. Not exist in Plaid.')),
                ('sort', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name_plural': 'institutions',
                'verbose_name': 'institution',
                'ordering': ['sort', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, editable=False)),
                ('guid', models.CharField(max_length=50, unique=True)),
                ('plaid_id', models.CharField(default=None, max_length=255, null=True, unique=True)),
                ('access_token', models.CharField(default=None, max_length=255, null=True, unique=True)),
                ('webhook', models.CharField(blank=True, default=None, max_length=50, null=True)),
                ('available_products', django.contrib.postgres.fields.jsonb.JSONField(default=None, null=True)),
                ('billed_products', django.contrib.postgres.fields.jsonb.JSONField(default=None, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('institution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.Institution')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'items',
                'verbose_name': 'item',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PlaidWebhook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=50)),
                ('code', models.CharField(max_length=50)),
                ('error', django.contrib.postgres.fields.jsonb.JSONField(default=None, null=True)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(default=None, null=True)),
                ('debug_info', models.TextField(blank=True, default=None, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='finance.Item')),
            ],
            options={
                'verbose_name_plural': 'webhooks',
                'verbose_name': 'webhook',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Stat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name_plural': 'stat',
                'verbose_name': 'stat',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, editable=False)),
                ('guid', models.CharField(max_length=100, unique=True)),
                ('plaid_id', models.CharField(max_length=100, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, default=None, max_digits=10, null=True)),
                ('date', models.DateField(default=None, null=True)),
                ('name', models.CharField(default=None, max_length=255, null=True)),
                ('transaction_type', models.CharField(default=None, max_length=50, null=True)),
                ('category', django.contrib.postgres.fields.jsonb.JSONField(default=None, null=True)),
                ('category_id', models.CharField(default=None, max_length=100, null=True)),
                ('pending', models.BooleanField(default=False)),
                ('pending_transaction_id', models.CharField(default=None, max_length=255, null=True)),
                ('payment_meta', django.contrib.postgres.fields.jsonb.JSONField(default=None, null=True)),
                ('location', django.contrib.postgres.fields.jsonb.JSONField(default=None, null=True)),
                ('roundup', models.DecimalField(decimal_places=2, default=None, help_text='Internal field. "Roundup" amount.', max_digits=5, null=True)),
                ('is_processed', models.NullBooleanField(default=False, help_text='Internal flag. Roundup has been transferred')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='finance.Account')),
            ],
            options={
                'verbose_name_plural': 'transactions',
                'verbose_name': 'transaction',
                'ordering': ['account', '-date'],
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
                'verbose_name': 'transfer prepare',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='account',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to='finance.Item'),
        ),
    ]
