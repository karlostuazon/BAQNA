# Generated by Django 3.1.7 on 2021-12-02 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0056_appointment_date_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
