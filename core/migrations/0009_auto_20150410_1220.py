# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20150407_1724'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='catinversion',
            options={'ordering': ['nombre'], 'verbose_name': 'Categoria de inversion', 'verbose_name_plural': 'Categorias de inversion'},
        ),
    ]
