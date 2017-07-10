# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lugar', '0006_auto_20150219_1533'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clasificacionmunic',
            name='color',
            field=models.CharField(max_length=30, null=True),
            preserve_default=True,
        ),
    ]
