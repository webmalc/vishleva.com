# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-18 16:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailing', '0002_auto_20170318_1937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sms',
            name='send_at',
            field=models.DateTimeField(db_index=True, null=True),
        ),
    ]
