# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-08-03 16:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0006_user_dwolla_verified_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='dwolla_verified_url',
            field=models.TextField(blank=True, null=True),
        ),
    ]
