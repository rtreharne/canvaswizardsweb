# Generated by Django 3.2.25 on 2024-04-17 06:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0029_auto_20240415_1335'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='supervisorset',
            name='types',
        ),
        migrations.AddField(
            model_name='supervisorset',
            name='type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='supervisor_set_types', to='projects.projecttype'),
        ),
    ]
