# Generated by Django 1.11.1 on 2017-08-04 12:54
from django.db import migrations, models

import waldur_ansible.playbook_jobs.models


class Migration(migrations.Migration):

    dependencies = [
        ('playbook_jobs', '0002_add_parameter_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='playbook',
            name='image',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=waldur_ansible.playbook_jobs.models.get_upload_path,
            ),
        ),
    ]
