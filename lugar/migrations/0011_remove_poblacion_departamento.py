# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lugar', '0010_poblacion_departamento'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='poblacion',
            name='departamento',
        ),
    ]
