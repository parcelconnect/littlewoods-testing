# Generated by Django 2.0.6 on 2019-02-12 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collector', '0012_auto_20160812_0948'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='proof_of_address_date_1',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='account',
            name='proof_of_address_date_2',
            field=models.DateField(null=True),
        ),
    ]
