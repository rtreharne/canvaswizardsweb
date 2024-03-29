# Generated by Django 3.2.24 on 2024-02-15 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0022_auto_20240215_0825'),
    ]

    operations = [
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('image', models.FileField(upload_to='portfolio/')),
                ('iframe', models.TextField(blank=True, null=True)),
                ('url', models.URLField(blank=True, null=True)),
            ],
        ),
    ]
