# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-09-04 16:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0017_transferbalance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='access_token',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='plaid_id',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
    ]
