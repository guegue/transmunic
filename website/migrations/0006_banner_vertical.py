# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0005_banner_imagen'),
    ]

    operations = [
        migrations.AddField(
            model_name='banner',
            name='vertical',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
