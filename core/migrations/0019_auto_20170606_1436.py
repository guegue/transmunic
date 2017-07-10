# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_catinversion_destacar'),
    ]

    operations = [
        migrations.AddField(
            model_name='catinversion',
            name='color',
            field=models.CharField(default=0, max_length=8),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='catinversion',
            name='destacar',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='proyecto',
            name='catinversion',
            field=models.ForeignKey(related_name='categoria_inversion', verbose_name='Categor\xeda de Inversi\xf3n', blank=True, to='core.CatInversion', null=True),
            preserve_default=True,
        ),
    ]
