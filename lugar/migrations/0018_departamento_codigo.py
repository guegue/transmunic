# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lugar', '0017_auto_20150527_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='departamento',
            name='codigo',
            field=models.CharField(max_length=15, verbose_name=b'Codigo', blank=True),
            preserve_default=True,
        ),
    ]
