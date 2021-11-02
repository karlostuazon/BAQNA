# Generated by Django 3.2.4 on 2021-11-01 03:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tracker', '0027_alter_appointment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='relationship',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='patient',
            name='username',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
