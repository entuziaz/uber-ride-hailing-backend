# Generated by Django 5.1.1 on 2024-10-06 22:58

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_app', '0002_alter_admin_admin_id_alter_admin_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='admin',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='admin',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
