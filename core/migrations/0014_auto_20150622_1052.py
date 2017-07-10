# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20150527_1621'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gasto',
            name='year',
        ),
        migrations.RemoveField(
            model_name='ingreso',
            name='year',
        ),
        migrations.RemoveField(
            model_name='inversion',
            name='year',
        ),
        migrations.RemoveField(
            model_name='inversionfuente',
            name='year',
        ),
        migrations.AddField(
            model_name='gasto',
            name='anio',
            field=models.IntegerField(default=0, verbose_name=b'Anio'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ingreso',
            name='anio',
            field=models.IntegerField(default=0, verbose_name=b'Anio'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inversion',
            name='anio',
            field=models.IntegerField(default=0, verbose_name=b'Anio'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inversionfuente',
            name='anio',
            field=models.IntegerField(default=0, verbose_name=b'Anio'),
            preserve_default=False,
        ),
    ]
