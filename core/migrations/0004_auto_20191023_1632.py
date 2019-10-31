# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20191023_1631'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pais',
            options={'ordering': ['name']},
        ),
    ]
