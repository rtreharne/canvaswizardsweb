# Generated by Django 3.2.24 on 2024-02-21 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('choices', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='module',
            name='credits',
            field=models.FloatField(),
        ),
    ]
