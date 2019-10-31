# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20191023_1632'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='persona',
            name='ciudad',
        ),
        migrations.DeleteModel(
            name='Ciudad',
        ),
        migrations.RemoveField(
            model_name='persona',
            name='paises',
        ),
        migrations.DeleteModel(
            name='Pais',
        ),
        migrations.DeleteModel(
            name='Persona',
        ),
    ]
