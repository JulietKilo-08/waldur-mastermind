# Generated by Django 2.2.13 on 2020-09-02 11:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('waldur_aws', '0002_immutable_default_json'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instance',
            name='description',
            field=models.CharField(
                blank=True, max_length=2000, verbose_name='description'
            ),
        ),
        migrations.AlterField(
            model_name='volume',
            name='description',
            field=models.CharField(
                blank=True, max_length=2000, verbose_name='description'
            ),
        ),
    ]
