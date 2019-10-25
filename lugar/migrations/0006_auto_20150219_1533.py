# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lugar', '0005_auto_20150219_1531'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clasificacionmunic',
            name='desde',
            field=models.DecimalField(null=True, verbose_name=b'Desde', max_digits=12, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='clasificacionmunic',
            name='hasta',
            field=models.DecimalField(null=True, verbose_name=b'Hasta', max_digits=12, decimal_places=2, blank=True),
            preserve_default=True,
        ),
    ]
