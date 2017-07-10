# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lugar', '0008_auto_20150310_1249'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='poblacion',
            name='departamento',
        ),
        migrations.AlterField(
            model_name='poblacion',
            name='municipio',
            field=models.ForeignKey(default=2, to='lugar.Municipio'),
            preserve_default=False,
        ),
    ]
