# Generated by Django 1.11.7 on 2017-12-27 08:36
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('waldur_jira', '0005_drop_impact_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='parent',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='waldur_jira.Issue',
            ),
        ),
        migrations.AddField(
            model_name='issuetype',
            name='subtask',
            field=models.BooleanField(default=False),
        ),
    ]
