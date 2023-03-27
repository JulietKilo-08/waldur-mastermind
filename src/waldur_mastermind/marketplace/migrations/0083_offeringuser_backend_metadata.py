# Generated by Django 3.2.18 on 2023-03-21 12:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('marketplace', '0082_offeringuser_propagation_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='offeringuser',
            name='backend_metadata',
            field=models.JSONField(
                blank=True, default=dict, help_text='Backend attributes of the user'
            ),
        ),
    ]
