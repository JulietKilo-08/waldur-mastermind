# Generated by Django 3.2.12 on 2022-02-07 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openstack_tenant', '0023_servergroup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servergroup',
            name='policy',
            field=models.CharField(
                blank=True, choices=[('affinity', 'Affinity')], max_length=40
            ),
        ),
    ]
