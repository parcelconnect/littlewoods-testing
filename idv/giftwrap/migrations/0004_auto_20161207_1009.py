# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2016-12-07 10:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('giftwrap', '0003_auto_20161206_1712'),
    ]

    operations = [
        migrations.RenameField(
            model_name='giftwraprequest',
            old_name='divert_address',
            new_name='divert_address1',
        ),
    ]
