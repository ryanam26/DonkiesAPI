# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-05-04 18:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0004_lender'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='is_primary',
            field=models.BooleanField(default=False),
        ),
    ]
