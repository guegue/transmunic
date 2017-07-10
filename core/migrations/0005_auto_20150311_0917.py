# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pixelfields_smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20150311_0912'),
    ]

    operations = [
        migrations.AddField(
            model_name='fuentefmto',
            name='tipofuente',
            field=models.ForeignKey(default=1, to='core.TipoFuenteFmto'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='inversionfuentedetalle',
            name='fuente',
            field=pixelfields_smart_selects.db_fields.ChainedForeignKey(blank=True, to='core.FuenteFmto', null=True),
            preserve_default=True,
        ),
    ]
