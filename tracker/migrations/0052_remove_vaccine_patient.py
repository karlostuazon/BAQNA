# Generated by Django 3.1.7 on 2021-11-29 19:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0051_vaccine_patient'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vaccine',
            name='patient',
        ),
    ]
