# Generated by Django 5.0.5 on 2025-01-22 13:28

from django.core.management import call_command
from django.db import migrations


def load_fixture(apps, schema_editor):
    call_command('loaddata', 'initial_data.json')

class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_alter_goal_end_month'),
    ]

    operations = [
    ]
