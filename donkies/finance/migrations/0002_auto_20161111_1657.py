# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-11 16:57
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('finance', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='member',
            unique_together=set([('user', 'institution')]),
        ),
    ]
