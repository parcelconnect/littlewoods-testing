# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-17 11:06
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collector', '0003_credential_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='credential',
            name='missing_from_s3',
        ),
    ]
