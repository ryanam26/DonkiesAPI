# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-08-08 12:45
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0012_user_funding_sources_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='funding_sources_url',
        ),
    ]