# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20150410_1220'),
    ]

    operations = [
        migrations.AddField(
            model_name='gasto',
            name='periodo',
            field=models.CharField(default=0, max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gasto',
            name='year',
            field=models.IntegerField(default=2000),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ingreso',
            name='periodo',
            field=models.CharField(default=0, max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ingreso',
            name='year',
            field=models.IntegerField(default=2000),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inversion',
            name='periodo',
            field=models.CharField(default=0, max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inversion',
            name='year',
            field=models.IntegerField(default=2000),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inversionfuente',
            name='periodo',
            field=models.CharField(default=0, max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inversionfuente',
            name='year',
            field=models.IntegerField(default=2000),
            preserve_default=False,
        ),
    ]
