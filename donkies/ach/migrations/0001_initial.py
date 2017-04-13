# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-04-13 21:36
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('finance', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChargeLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=None, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.Account')),
            ],
            options={
                'verbose_name_plural': 'charge logs',
                'verbose_name': 'charge log',
                'ordering': ['-created_at'],
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
                'verbose_name': 'transfer debt',
                'ordering': ['-processed_at'],
            },
        ),
        migrations.CreateModel(
            name='TransferStripe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_id', models.CharField(max_length=100, unique=True)),
                ('status', models.CharField(choices=[('pending', 'pending'), ('succeeded', 'succeeded'), ('failed', 'failed')], default='pending', max_length=9)),
                ('amount_stripe', models.IntegerField(help_text='Amount in cents.')),
                ('balance_transaction', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('currency', models.CharField(default='usd', max_length=3)),
                ('captured', models.BooleanField(default=True)),
                ('description', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('failure_code', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('failure_message', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('livemode', models.BooleanField(default=False)),
                ('metadata', django.contrib.postgres.fields.jsonb.JSONField(default=None, null=True)),
                ('paid', models.BooleanField(default=False)),
                ('source', django.contrib.postgres.fields.jsonb.JSONField(default=None, null=True)),
                ('created_at', models.DateTimeField(default=None, null=True)),
                ('amount', models.DecimalField(decimal_places=2, default=None, max_digits=10, null=True)),
                ('is_processed_to_user', models.BooleanField(default=False, help_text='Funds processed to TransferUser model.')),
                ('processed_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='charges', to='finance.Account')),
            ],
            options={
                'verbose_name_plural': 'charges',
                'verbose_name': 'charge',
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='TransferUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cached_amount', models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=10, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('items', models.ManyToManyField(to='ach.TransferStripe')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'transfers user',
                'verbose_name': 'transfer user',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='transferdebt',
            name='tu',
            field=models.ForeignKey(help_text='TransferUser transfer', on_delete=django.db.models.deletion.CASCADE, to='ach.TransferUser'),
        ),
    ]
