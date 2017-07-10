# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0008_documento_titulo'),
    ]

    operations = [
        migrations.AddField(
            model_name='banner',
            name='color',
            field=models.CharField(default=0, max_length=6),
            preserve_default=False,
        ),
    ]
