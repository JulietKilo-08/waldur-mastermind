# Generated by Django 2.2.13 on 2020-11-13 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openstack', '0013_securitygrouprule_direction'),
    ]

    operations = [
        migrations.AddField(
            model_name='securitygrouprule',
            name='ethertype',
            field=models.CharField(
                choices=[('IPv4', 'IPv4'), ('IPv6', 'IPv6')],
                default='IPv4',
                max_length=8,
            ),
        ),
    ]
