# Generated by Django 5.1.6 on 2025-03-16 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0012_fleet_fleetdocument'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='packaging_type',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='city',
            name='select_default_pricing_model',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='city',
            name='weekend_end_day',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='city',
            name='weekend_end_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='city',
            name='weekend_start_day',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='city',
            name='weekend_start_time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
