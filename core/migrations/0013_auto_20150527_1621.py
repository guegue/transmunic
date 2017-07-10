# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_anio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tipogasto',
            name='clasificacion',
            field=models.IntegerField(default=0, null=True, choices=[(b'0', b'Gasto Corriente'), (b'1', b'Gasto de Capital')]),
            preserve_default=True,
        ),
    ]
