# Generated by Django 3.1.7 on 2021-12-02 17:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0053_vaccine_patient'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patientvaccine',
            name='vaccine',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='patient_vaccine', to='tracker.vaccine'),
        ),
    ]
