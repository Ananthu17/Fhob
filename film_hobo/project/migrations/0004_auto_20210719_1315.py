# Generated by Django 3.1 on 2021-07-19 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0003_auto_20210719_0419'),
    ]

    operations = [
        migrations.AlterField(
            model_name='character',
            name='password',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
