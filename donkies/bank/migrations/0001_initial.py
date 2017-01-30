# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-30 15:40
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('finance', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.CharField(blank=True, default=None, max_length=50, null=True)),
                ('type', models.CharField(choices=[('personal', 'personal'), ('business', 'business')], default='personal', max_length=10)),
                ('dwolla_type', models.CharField(choices=[('personal', 'personal'), ('business', 'business'), ('unverified', 'unverified')], default='unverified', max_length=10)),
                ('dwolla_id', models.CharField(blank=True, default=None, max_length=50, null=True, unique=True)),
                ('status', models.CharField(choices=[('verified', 'verified'), ('unverified', 'unverified')], default='unverified', max_length=10)),
                ('created_at', models.DateTimeField(blank=True, default=None, help_text='Created at dwolla.', null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'customers',
                'verbose_name': 'customer',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='FundingSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dwolla_id', models.CharField(blank=True, default=None, max_length=50, null=True, unique=True)),
                ('account_number', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('routing_number', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('status', models.CharField(choices=[('verified', 'verified'), ('unverified', 'unverified')], default='unverified', max_length=10)),
                ('type', models.CharField(choices=[('checking', 'checking'), ('savings', 'savings')], max_length=8)),
                ('typeb', models.CharField(choices=[('bank', 'bank'), ('balance', 'balance')], default=None, max_length=7, null=True)),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('is_removed', models.BooleanField(default=False)),
                ('verification_type', models.CharField(choices=[('micro-deposit', 'micro deposit'), ('iav', 'instant verification')], default='micro-deposit', max_length=20)),
                ('md_status', models.CharField(blank=True, default=None, help_text='Micro-deposits verification status', max_length=20, null=True)),
                ('md_created_at', models.DateTimeField(blank=True, default=None, help_text='Micro-deposits created time.', null=True)),
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='finance.Account')),
            ],
            options={
                'verbose_name_plural': 'funding sources',
                'verbose_name': 'funding source',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='FundingSourceIAVLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dwolla_id', models.CharField(max_length=255, unique=True)),
                ('is_processed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.Account')),
            ],
            options={
                'verbose_name_plural': 'funding source iav logs',
                'verbose_name': 'funding source iav log',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='fundingsourceiavlog',
            unique_together=set([('account', 'dwolla_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='fundingsource',
            unique_together=set([('account', 'name')]),
        ),
    ]
