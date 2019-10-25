# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lugar', '0014_auto_20150517_2341'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='clasificacionmunicano',
            unique_together=set([('municipio', 'year')]),
        ),
    ]
