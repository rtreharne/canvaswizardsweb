# Generated by Django 3.2.25 on 2024-06-18 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0052_alter_student_mbiolsci'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='submitted_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
