# Generated by Django 3.2.25 on 2024-05-02 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0045_alter_supervisor_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='supervisor',
            name='max_projects',
            field=models.IntegerField(default=4),
        ),
    ]
