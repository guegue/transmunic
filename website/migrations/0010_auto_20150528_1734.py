# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0009_banner_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documento',
            name='titulo',
            field=models.CharField(max_length=220),
            preserve_default=True,
        ),
    ]
