# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-03-02 15:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_auto_20200218_1545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gasto',
            name='fecha',
            field=models.DateField(verbose_name=b'Fecha de entrada'),
        ),
        migrations.AlterField(
            model_name='ingreso',
            name='fecha',
            field=models.DateField(verbose_name=b'Fecha de entrada'),
        ),
        migrations.AlterField(
            model_name='inversion',
            name='fecha',
            field=models.DateField(verbose_name=b'Fecha de entrada'),
        ),
        migrations.AlterField(
            model_name='inversionfuente',
            name='fecha',
            field=models.DateField(verbose_name=b'Fecha de entrada'),
        ),
        migrations.AlterField(
            model_name='subsubtipogasto',
            name='clasificacion',
            field=models.IntegerField(choices=[(0, b'Gasto Corriente'), (1, b'Gasto de Capital'), (2, b'Otra')], default=0, null=True),
        ),
        migrations.AlterField(
            model_name='tipogasto',
            name='clasificacion',
            field=models.IntegerField(choices=[(0, b'Gasto Corriente'), (1, b'Gasto de Capital')], default=0, null=True),
        ),
        migrations.AlterField(
            model_name='transferencia',
            name='fecha',
            field=models.DateField(verbose_name=b'Fecha de entrada'),
        ),
    ]
