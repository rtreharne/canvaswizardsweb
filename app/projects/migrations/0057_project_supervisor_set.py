# Generated by Django 3.2.25 on 2024-09-01 07:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0056_remove_project_supervisor_set'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='supervisor_set',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='projects.supervisorset'),
        ),
    ]
