# Generated by Django 3.2.23 on 2024-01-17 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0008_event_playlist'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='mailing_list',
            field=models.BooleanField(default=False, verbose_name='Join our mailing list?'),
        ),
    ]
