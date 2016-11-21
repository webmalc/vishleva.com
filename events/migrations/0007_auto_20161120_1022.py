# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-20 07:22
from __future__ import unicode_literals

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_auto_20161118_1201'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='client',
            options={'ordering': ['last_name', 'first_name']},
        ),
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ['begin']},
        ),
        migrations.AlterField(
            model_name='client',
            name='last_name',
            field=models.CharField(blank=True, db_index=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='phone',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, db_index=True, max_length=30, null=True, unique=True),
        ),
    ]