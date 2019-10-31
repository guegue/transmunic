# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lugar', '0013_auto_20150515_0059'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='clasificacionmunicano',
            unique_together=set([('municipio', 'clasificacion', 'year')]),
        ),
    ]
