# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_ciudad_pais_persona'),
    ]

    operations = [
        migrations.AlterField(
            model_name='persona',
            name='paises',
            field=models.ManyToManyField(to='core.Pais', verbose_name='pais'),
            preserve_default=True,
        ),
    ]
