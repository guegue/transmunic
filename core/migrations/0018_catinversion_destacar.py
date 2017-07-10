# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20151203_1405'),
    ]

    operations = [
        migrations.AddField(
            model_name='catinversion',
            name='destacar',
            field=models.BooleanField(default=0),
            preserve_default=False,
        ),
    ]
