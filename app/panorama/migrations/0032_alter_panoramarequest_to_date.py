# Generated by Django 3.2.25 on 2024-11-11 17:45

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panorama', '0031_alter_panoramarequest_to_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='panoramarequest',
            name='to_date',
            field=models.DateField(blank=True, default=datetime.date(2024, 11, 11), null=True),
        ),
    ]