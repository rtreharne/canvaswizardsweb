# Generated by Django 3.2.25 on 2024-04-12 09:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0023_auto_20240412_0934'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='second_supervisor',
        ),
        migrations.RemoveField(
            model_name='project',
            name='student',
        ),
    ]