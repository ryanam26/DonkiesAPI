# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-17 10:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='institution',
            name='medium_logo_url',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='institution',
            name='small_logo_url',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
    ]
