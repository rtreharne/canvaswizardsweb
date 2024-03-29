# Generated by Django 3.2.23 on 2024-01-18 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0010_auto_20240117_0858'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='online_info',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='registration',
            name='mode',
            field=models.CharField(blank=True, choices=[('In Person', 'In Person'), ('Online', 'Online')], default='In Person', max_length=100, null=True),
        ),
    ]
