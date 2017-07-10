# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20150517_0822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gasto',
            name='year',
            field=models.IntegerField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ingreso',
            name='year',
            field=models.IntegerField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='inversion',
            name='year',
            field=models.IntegerField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='inversionfuente',
            name='year',
            field=models.IntegerField(),
            preserve_default=True,
        ),
    ]
