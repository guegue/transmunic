# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_origengasto'),
    ]

    operations = [
        migrations.AddField(
            model_name='subsubtipogasto',
            name='origen',
            field=models.ForeignKey(related_name='origen', to='core.OrigenGasto', null=True),
            preserve_default=True,
        ),
    ]
