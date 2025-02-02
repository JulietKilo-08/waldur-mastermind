# Generated by Django 3.2.20 on 2023-11-17 11:27

import django.db.models.deletion
import django.utils.timezone
import django_fsm
import model_utils.fields
from django.db import migrations, models

import waldur_core.core.fields
import waldur_core.core.validators


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('marketplace', '0104_translations'),
        ('structure', '0040_useragreement_uuid'),
    ]

    operations = [
        migrations.CreateModel(
            name='Call',
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
                        blank=True, max_length=2000, verbose_name='description'
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
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                (
                    'round_strategy',
                    django_fsm.FSMIntegerField(
                        choices=[(1, 'One-time'), (2, 'Regular')], default=2
                    ),
                ),
                (
                    'review_strategy',
                    django_fsm.FSMIntegerField(
                        choices=[
                            (1, 'After round is closed'),
                            (2, 'After application submission'),
                        ],
                        default=1,
                    ),
                ),
                (
                    'allocation_strategy',
                    django_fsm.FSMIntegerField(
                        choices=[
                            (1, 'By call manager'),
                            (2, 'Automatic based on review scoring'),
                        ],
                        default=2,
                    ),
                ),
                (
                    'state',
                    django_fsm.FSMIntegerField(
                        choices=[(1, 'Draft'), (2, 'Active'), (3, 'Archived')],
                        default=1,
                    ),
                ),
                ('offerings', models.ManyToManyField(to='marketplace.Offering')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Proposal',
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
                    'name',
                    models.CharField(
                        max_length=150,
                        validators=[waldur_core.core.validators.validate_name],
                        verbose_name='name',
                    ),
                ),
                ('uuid', waldur_core.core.fields.UUIDField()),
                (
                    'state',
                    django_fsm.FSMIntegerField(
                        choices=[(1, 'Draft'), (2, 'Active'), (3, 'Cancelled')],
                        default=1,
                    ),
                ),
                ('duration_requested', models.DateTimeField()),
                ('resource_usage', models.JSONField()),
                (
                    'project',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to='structure.project',
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Review',
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
                ('uuid', waldur_core.core.fields.UUIDField()),
                (
                    'state',
                    django_fsm.FSMIntegerField(
                        choices=[(1, 'Draft'), (2, 'Active'), (3, 'Cancelled')],
                        default=1,
                    ),
                ),
                ('points', models.CharField(blank=True, max_length=255)),
                ('type', models.CharField(blank=True, max_length=255)),
                ('version', models.CharField(blank=True, max_length=255)),
                (
                    'proposal',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to='proposal.proposal',
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Round',
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
                ('uuid', waldur_core.core.fields.UUIDField()),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                (
                    'call',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to='proposal.call'
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ReviewComment',
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
                ('uuid', waldur_core.core.fields.UUIDField()),
                ('message', models.CharField(max_length=255)),
                (
                    'review',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='proposal.review',
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ResourceAllocator',
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
                    'name',
                    models.CharField(
                        max_length=150,
                        validators=[waldur_core.core.validators.validate_name],
                        verbose_name='name',
                    ),
                ),
                ('uuid', waldur_core.core.fields.UUIDField()),
                (
                    'call',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='proposal.call'
                    ),
                ),
                (
                    'project',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='structure.project',
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='proposal',
            name='round',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to='proposal.round'
            ),
        ),
    ]
