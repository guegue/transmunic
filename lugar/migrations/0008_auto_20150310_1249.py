# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pixelfields_smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('lugar', '0007_auto_20150219_1534'),
    ]

    operations = [
        migrations.CreateModel(
            name='Poblacion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('anio', models.IntegerField()),
                ('poblacion', models.IntegerField()),
                ('departamento', models.ForeignKey(to='lugar.Departamento')),
                ('municipio', pixelfields_smart_selects.db_fields.ChainedForeignKey(blank=True, to='lugar.Municipio', null=True)),
            ],
            options={
                'ordering': ['anio'],
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='municipio',
            name='poblacion',
        ),
    ]
