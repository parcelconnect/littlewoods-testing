# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-02-01 12:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('giftwrap', '0009_auto_20170120_1029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='giftwraprequest',
            name='card_message',
            field=models.TextField(blank=True, max_length=80),
        ),
    ]
