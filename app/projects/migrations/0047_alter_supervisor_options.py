# Generated by Django 3.2.25 on 2024-05-09 11:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0046_supervisor_max_projects'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='supervisor',
            options={'ordering': ['username']},
        ),
    ]
