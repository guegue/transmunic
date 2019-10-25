# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lugar', '0018_departamento_codigo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='municipio',
            name='slug',
            field=autoslug.fields.AutoSlugField(verbose_name=b'municipio', editable=False),
            preserve_default=True,
        ),
    ]
