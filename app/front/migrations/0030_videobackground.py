# Generated by Django 3.2.25 on 2024-05-16 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0029_alter_portfolio_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoBackground',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('file', models.FileField(upload_to='icons/')),
            ],
        ),
    ]
