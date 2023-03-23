# Generated by Django 2.2.13 on 2020-12-18 12:06

import django.db.models.deletion
import django_fsm
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('marketplace', '0001_squashed_0076'),
        ('google', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoogleCalendar',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('error_message', models.TextField(blank=True)),
                ('error_traceback', models.TextField(blank=True)),
                (
                    'state',
                    django_fsm.FSMIntegerField(
                        choices=[
                            (5, 'Creation Scheduled'),
                            (6, 'Creating'),
                            (1, 'Update Scheduled'),
                            (2, 'Updating'),
                            (7, 'Deletion Scheduled'),
                            (8, 'Deleting'),
                            (3, 'OK'),
                            (4, 'Erred'),
                        ],
                        default=5,
                    ),
                ),
                (
                    'backend_id',
                    models.CharField(
                        blank=True, db_index=True, max_length=255, null=True
                    ),
                ),
                ('public', models.BooleanField(default=False)),
                (
                    'offering',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='marketplace.Offering',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Google calendar',
                'verbose_name_plural': 'Google calendars',
            },
        ),
    ]
