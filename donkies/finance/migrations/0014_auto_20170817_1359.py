# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-08-17 13:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0013_fundingsource_item'),
    ]

    operations = [
        migrations.AddField(
            model_name='transfercalculation',
            name='applied_funds',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='transfercalculation',
            name='total_in_stash_account',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, null=True),
        ),
    ]
