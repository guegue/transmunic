# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20150311_0917'),
    ]

    operations = [
        migrations.AddField(
            model_name='inversion',
            name='nombremunic',
            field=models.CharField(default=1, max_length=250),
            preserve_default=False,
        ),
    ]
