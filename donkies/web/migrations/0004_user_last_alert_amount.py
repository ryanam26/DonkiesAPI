# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-06-26 14:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_user_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_alert_amount',
            field=models.IntegerField(default=0, help_text='Last alert roundup amount. 5, 10, 15 etc'),
        ),
    ]