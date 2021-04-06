# Generated by Django 3.1.7 on 2021-04-06 04:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hobo_user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='eyes',
            field=models.CharField(blank=True, choices=[('BLK', 'Black'), ('BRO', 'Brown'), ('BLU', 'Blue'), ('GRE', 'Green'), ('HAS', 'Hasel')], max_length=150, null=True, verbose_name='Eyes'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='hair_color',
            field=models.CharField(blank=True, choices=[('AUR', 'Auburn/Red'), ('BLA', 'Black'), ('BLO', 'Blonde'), ('BRO', 'Brown'), ('SAP', 'Salt and Pepper'), ('GOW', 'Gray/White')], max_length=150, null=True, verbose_name='Hair Color'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='hair_length',
            field=models.CharField(blank=True, choices=[('BOS', 'Bald/Shaved'), ('SHO', 'Short'), ('MED', 'Medium'), ('LON', 'Long'), ('CUR', 'Curly'), ('AFR', 'Afro')], max_length=150, null=True, verbose_name='Hair Length'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='physique',
            field=models.CharField(blank=True, choices=[('ATH', 'Athletic'), ('SLE', 'Slender'), ('MED', 'Medium'), ('HEA', 'Heavy')], max_length=150, null=True, verbose_name='Physique'),
        ),
    ]
