# Generated by Django 3.1.7 on 2021-10-18 11:11

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0011_auto_20211018_1841'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='physician',
            name='user',
        ),
        migrations.AlterField(
            model_name='parents',
            name='contact',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None),
        ),
        migrations.AlterField(
            model_name='physician',
            name='cell_no',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None),
        ),
    ]
