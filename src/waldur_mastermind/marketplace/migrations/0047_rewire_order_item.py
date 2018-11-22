# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-20 13:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0046_migrate_resource'),
    ]

    operations = [
        migrations.AlterField(
            model_name='componentquota',
            name='resource',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quotas',
                                    to='marketplace.Resource'),
        ),
        migrations.AlterField(
            model_name='componentusage',
            name='resource',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usages',
                                    to='marketplace.Resource'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='state',
            field=django_fsm.FSMIntegerField(choices=[(1, 'pending'), (2, 'executing'), (3, 'done'), (4, 'erred')],
                                             default=1),
        ),
        migrations.AlterField(
            model_name='resource',
            name='offering',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+',
                                    to='marketplace.Offering'),
        ),
        migrations.AlterUniqueTogether(
            name='componentquota',
            unique_together=set([('resource', 'component')]),
        ),
        migrations.AlterUniqueTogether(
            name='componentusage',
            unique_together=set([('resource', 'component', 'date')]),
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='object_id',
        ),
        migrations.RemoveField(
            model_name='componentusage',
            name='order_item',
        ),
        migrations.RemoveField(
            model_name='componentquota',
            name='order_item',
        ),
    ]
