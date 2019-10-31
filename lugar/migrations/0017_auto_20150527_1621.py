# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lugar', '0016_auto_20150519_1210'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='municipio',
            options={'ordering': ['nombre']},
        ),
        migrations.AddField(
            model_name='clasificacionmunic',
            name='minimo_inversion',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
    ]
