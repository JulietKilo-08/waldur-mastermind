# Generated by Django 1.11.1 on 2017-11-29 12:44
import django.db.models.deletion
import django.utils.timezone
import django_fsm
import model_utils.fields
from django.db import migrations, models

import waldur_core.core.fields
import waldur_core.core.models
import waldur_core.core.shims
import waldur_core.core.validators
import waldur_core.logging.loggers


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('structure', '0001_squashed_0036'),
    ]

    operations = [
        migrations.CreateModel(
            name='Droplet',
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
                (
                    'created',
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name='created',
                    ),
                ),
                (
                    'modified',
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name='modified',
                    ),
                ),
                (
                    'description',
                    models.CharField(
                        blank=True, max_length=500, verbose_name='description'
                    ),
                ),
                (
                    'name',
                    models.CharField(
                        max_length=150,
                        validators=[waldur_core.core.validators.validate_name],
                        verbose_name='name',
                    ),
                ),
                ('uuid', waldur_core.core.fields.UUIDField()),
                ('error_message', models.TextField(blank=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                (
                    'runtime_state',
                    models.CharField(
                        blank=True, max_length=150, verbose_name='runtime state'
                    ),
                ),
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
                ('backend_id', models.CharField(blank=True, max_length=255)),
                (
                    'cores',
                    models.PositiveSmallIntegerField(
                        default=0, help_text='Number of cores in a VM'
                    ),
                ),
                (
                    'ram',
                    models.PositiveIntegerField(
                        default=0, help_text='Memory size in MiB'
                    ),
                ),
                (
                    'disk',
                    models.PositiveIntegerField(
                        default=0, help_text='Disk size in MiB'
                    ),
                ),
                (
                    'min_ram',
                    models.PositiveIntegerField(
                        default=0, help_text='Minimum memory size in MiB'
                    ),
                ),
                (
                    'min_disk',
                    models.PositiveIntegerField(
                        default=0, help_text='Minimum disk size in MiB'
                    ),
                ),
                ('image_name', models.CharField(blank=True, max_length=150)),
                ('key_name', models.CharField(blank=True, max_length=50)),
                ('key_fingerprint', models.CharField(blank=True, max_length=47)),
                (
                    'user_data',
                    models.TextField(
                        blank=True,
                        help_text='Additional data that will be added to instance on provisioning',
                    ),
                ),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                (
                    'transfer',
                    models.PositiveIntegerField(
                        default=0, help_text='Amount of transfer bandwidth in MiB'
                    ),
                ),
                (
                    'ip_address',
                    models.GenericIPAddressField(
                        blank=True, null=True, protocol='IPv4'
                    ),
                ),
                ('region_name', models.CharField(blank=True, max_length=150)),
                ('size_name', models.CharField(blank=True, max_length=150)),
            ],
            options={
                'abstract': False,
            },
            bases=(
                waldur_core.core.models.DescendantMixin,
                waldur_core.core.models.BackendModelMixin,
                waldur_core.logging.loggers.LoggableMixin,
                models.Model,
            ),
        ),
        migrations.CreateModel(
            name='Image',
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
                (
                    'name',
                    models.CharField(
                        max_length=150,
                        validators=[waldur_core.core.validators.validate_name],
                        verbose_name='name',
                    ),
                ),
                ('uuid', waldur_core.core.fields.UUIDField()),
                ('backend_id', models.CharField(max_length=255, unique=True)),
                ('distribution', models.CharField(max_length=100)),
                ('type', models.CharField(max_length=100)),
                (
                    'is_official',
                    models.BooleanField(
                        default=False, help_text='Is image provided by DigitalOcean'
                    ),
                ),
                (
                    'min_disk_size',
                    models.PositiveIntegerField(
                        help_text='Minimum disk required for a size to use this image',
                        null=True,
                    ),
                ),
                ('created_at', models.DateTimeField(null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(waldur_core.core.models.BackendModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Region',
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
                (
                    'name',
                    models.CharField(
                        max_length=150,
                        validators=[waldur_core.core.validators.validate_name],
                        verbose_name='name',
                    ),
                ),
                ('uuid', waldur_core.core.fields.UUIDField()),
                ('backend_id', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(waldur_core.core.models.BackendModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Size',
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
                (
                    'name',
                    models.CharField(
                        max_length=150,
                        validators=[waldur_core.core.validators.validate_name],
                        verbose_name='name',
                    ),
                ),
                ('uuid', waldur_core.core.fields.UUIDField()),
                ('backend_id', models.CharField(max_length=255, unique=True)),
                (
                    'cores',
                    models.PositiveSmallIntegerField(
                        help_text='Number of cores in a VM'
                    ),
                ),
                ('ram', models.PositiveIntegerField(help_text='Memory size in MiB')),
                ('disk', models.PositiveIntegerField(help_text='Disk size in MiB')),
                (
                    'transfer',
                    models.PositiveIntegerField(
                        help_text='Amount of transfer bandwidth in MiB'
                    ),
                ),
                (
                    'price',
                    models.DecimalField(
                        decimal_places=5,
                        default=0,
                        max_digits=11,
                        verbose_name='Hourly price rate',
                    ),
                ),
                ('regions', models.ManyToManyField(to='waldur_digitalocean.Region')),
            ],
            options={
                'abstract': False,
            },
            bases=(waldur_core.core.models.BackendModelMixin, models.Model),
        ),
        migrations.AddField(
            model_name='image',
            name='regions',
            field=models.ManyToManyField(to='waldur_digitalocean.Region'),
        ),
    ]
