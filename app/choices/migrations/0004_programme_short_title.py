# Generated by Django 3.2.24 on 2024-02-22 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('choices', '0003_auto_20240221_1304'),
    ]

    operations = [
        migrations.AddField(
            model_name='programme',
            name='short_title',
            field=models.CharField(blank=True, max_length=28, null=True),
        ),
    ]
