# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-19 13:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailing', '0006_auto_20170413_1632'),
    ]

    operations = [
        migrations.AddField(
            model_name='sms',
            name='send_before',
            field=models.DateTimeField(db_index=True, null=True),
        ),
    ]
