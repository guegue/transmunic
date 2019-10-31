# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('lugar', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='comarca',
            name='departamento',
            field=models.ForeignKey(default=1, to='lugar.Departamento'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='comarca',
            name='municipio',
            field=smart_selects.db_fields.ChainedForeignKey(chained_model_field=b'nombre', chained_field=b'depto', blank=True, to='lugar.Municipio', null=True),
            preserve_default=True,
        ),
    ]
