# Generated by Django 3.2.25 on 2024-04-10 10:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0017_student_institution'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('admin_dept', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='project_type_admin_dept', to='projects.department')),
                ('institution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.institution')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectKeyword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('admin_dept', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='project_keyword_admin_dept', to='projects.department')),
                ('institution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.institution')),
            ],
        ),
        migrations.AddConstraint(
            model_name='projecttype',
            constraint=models.UniqueConstraint(fields=('name', 'admin_dept'), name='unique_project_type'),
        ),
        migrations.AddConstraint(
            model_name='projectkeyword',
            constraint=models.UniqueConstraint(fields=('name', 'admin_dept'), name='unique_project_keyword'),
        ),
    ]
