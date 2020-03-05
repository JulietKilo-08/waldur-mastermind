# Generated by Django 1.11.21 on 2019-07-25 07:19
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('structure', '0009_project_is_removed'),
        ('waldur_vmware', '0016_port'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerNetworkPair',
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
                    'customer',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='structure.Customer',
                    ),
                ),
                (
                    'network',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='waldur_vmware.Network',
                    ),
                ),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='customernetworkpair', unique_together=set([('customer', 'network')]),
        ),
    ]
