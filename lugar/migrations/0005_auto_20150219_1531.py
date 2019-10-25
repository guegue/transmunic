# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('lugar', '0004_clasificacionmunic_fecha'),
    ]

    operations = [
        migrations.RenameField(
            model_name='clasificacionmunic',
            old_name='fecha',
            new_name='fecha_desde',
        ),
        migrations.AddField(
            model_name='clasificacionmunic',
            name='fecha_hasta',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
