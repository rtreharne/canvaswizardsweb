# Generated by Django 3.2.25 on 2024-03-19 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0010_auto_20240319_0921'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportrequest',
            name='assignment_name',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
