# Generated by Django 3.2.25 on 2024-07-14 10:40

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('presentations', '0002_auto_20240714_0808'),
    ]

    operations = [
        migrations.AddField(
            model_name='presentationrequest',
            name='uuid',
            field=models.UUIDField(blank=True, default=uuid.uuid4, editable=False, null=True),
        ),
    ]