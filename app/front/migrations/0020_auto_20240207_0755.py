# Generated by Django 3.2.23 on 2024-02-07 07:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0019_event_ask_for_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='description',
        ),
        migrations.AddField(
            model_name='registration',
            name='description',
            field=models.TextField(blank=True, help_text='Please describe your issue in as much detail as possible. The more we know, the better we can help you.', null=True, verbose_name="What's your issue?"),
        ),
    ]
