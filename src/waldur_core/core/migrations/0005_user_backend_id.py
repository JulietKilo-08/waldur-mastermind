# Generated by Django 1.11.18 on 2019-02-25 08:38
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_user_details'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='backend_id',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
