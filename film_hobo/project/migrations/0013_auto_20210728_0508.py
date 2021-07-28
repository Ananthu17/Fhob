# Generated by Django 3.1 on 2021-07-28 05:08

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0012_sides_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sides',
            name='description',
        ),
        migrations.AlterField(
            model_name='sides',
            name='scene_1',
            field=ckeditor.fields.RichTextField(blank=True, null=True, verbose_name='Scene Description'),
        ),
        migrations.AlterField(
            model_name='sides',
            name='scene_2',
            field=ckeditor.fields.RichTextField(blank=True, null=True, verbose_name='Scene Description'),
        ),
        migrations.AlterField(
            model_name='sides',
            name='scene_3',
            field=ckeditor.fields.RichTextField(blank=True, null=True, verbose_name='Scene Description'),
        ),
    ]
