# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_catinversion_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='catinversion',
            name='shortname',
            field=models.CharField(max_length=25, null=True, blank=True),
            preserve_default=True,
        ),
    ]
