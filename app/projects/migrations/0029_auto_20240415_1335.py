# Generated by Django 3.2.25 on 2024-04-15 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0028_alter_supervisor_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='institute',
            name='logo',
        ),
        migrations.AddField(
            model_name='institution',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='institute_logos/'),
        ),
    ]
