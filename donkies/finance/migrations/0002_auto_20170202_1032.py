# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-02 10:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Stat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'ordering': ['id'],
                'verbose_name': 'stat',
                'verbose_name_plural': 'stat',
            },
        ),
        migrations.AlterModelOptions(
            name='transferdonkies',
            options={'ordering': ['-updated_at'], 'verbose_name': 'transfer donkies', 'verbose_name_plural': 'transfers donkies'},
        ),
    ]