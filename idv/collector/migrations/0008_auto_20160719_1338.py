# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-07-19 13:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collector', '0007_auto_20160519_0900'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='account_number',
            field=models.CharField(max_length=8),
        ),
    ]