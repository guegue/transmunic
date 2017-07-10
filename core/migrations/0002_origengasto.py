# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrigenGasto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=200)),
                ('slug', autoslug.fields.AutoSlugField(editable=False)),
            ],
            options={
                'ordering': ['nombre'],
                'verbose_name_plural': 'Origen  de los gastos',
            },
            bases=(models.Model,),
        ),
    ]
