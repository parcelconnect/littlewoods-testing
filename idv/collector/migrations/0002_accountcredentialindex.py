# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-08 13:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('collector', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountCredentialIndex',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.IntegerField(default=0)),
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='collector.Account')),
            ],
        ),
    ]