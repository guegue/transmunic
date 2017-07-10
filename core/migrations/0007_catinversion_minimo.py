# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_inversion_nombremunic'),
    ]

    operations = [
        migrations.AddField(
            model_name='catinversion',
            name='minimo',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
