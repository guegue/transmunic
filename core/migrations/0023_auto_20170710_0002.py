# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_auto_20170708_2307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catinversion',
            name='slug',
            field=models.SlugField(max_length=80),
            preserve_default=True,
        ),
    ]
