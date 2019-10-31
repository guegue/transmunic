# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lugar', '0009_auto_20150310_1254'),
    ]

    operations = [
        migrations.AddField(
            model_name='poblacion',
            name='departamento',
            field=models.ForeignKey(default=1, to='lugar.Departamento'),
            preserve_default=False,
        ),
    ]
