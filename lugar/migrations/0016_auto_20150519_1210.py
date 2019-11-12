# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lugar', '0015_auto_20150517_2341'),
    ]

    operations = [
        migrations.RenameField(
            model_name='clasificacionmunicano',
            old_name='year',
            new_name='anio',
        ),
        migrations.AlterField(
            model_name='clasificacionmunicano',
            name='clasificacion',
            field=models.ForeignKey(related_name='clase', to='lugar.ClasificacionMunic'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='clasificacionmunicano',
            name='municipio',
            field=models.ForeignKey(related_name='clase', to='lugar.Municipio'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='clasificacionmunicano',
            unique_together=set([('municipio', 'anio')]),
        ),
    ]
