# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pixelfields_smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('lugar', '0002_auto_20141209_2257'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comarca',
            name='municipio',
            field=pixelfields_smart_selects.db_fields.ChainedForeignKey(blank=True, to='lugar.Municipio', null=True),
            preserve_default=True,
        ),
    ]
