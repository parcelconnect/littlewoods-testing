# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-22 09:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('giftwrap', '0011_auto_20170201_1344'),
    ]

    operations = [
        migrations.RenameField(
            model_name='giftwraprequest',
            old_name='updated_at',
            new_name='modified_at',
        ),
    ]
