# Generated by Django 5.0.5 on 2025-01-25 11:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_goal_end_month'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goal',
            name='end_month',
            field=models.DateField(default=datetime.datetime(2026, 1, 25, 11, 54, 0, 322596, tzinfo=datetime.timezone.utc), null=True),
        ),
    ]
