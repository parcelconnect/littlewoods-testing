# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2016-12-05 11:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('giftwrap', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='giftwraprequest',
            name='product_description',
            field=models.TextField(max_length=500),
        ),
    ]
