# Generated by Django 3.2.25 on 2024-04-10 07:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_programme_institution'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='institution',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='projects.institution'),
        ),
    ]