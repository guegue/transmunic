# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ClasificacionMunic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('clasificacion', models.CharField(max_length=120)),
                ('desde', models.DecimalField(null=True, verbose_name=b'Desde', max_digits=10, decimal_places=5, blank=True)),
                ('hasta', models.DecimalField(null=True, verbose_name=b'Hasta', max_digits=10, decimal_places=5, blank=True)),
                ('color', models.CharField(max_length=30)),
            ],
            options={
                'ordering': ['clasificacion'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Comarca',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=120)),
                ('slug', autoslug.fields.AutoSlugField(editable=False)),
                ('poblacion', models.IntegerField()),
                ('latitud', models.DecimalField(null=True, verbose_name=b'Latitud', max_digits=10, decimal_places=6, blank=True)),
                ('longitud', models.DecimalField(null=True, verbose_name=b'Longitud', max_digits=10, decimal_places=6, blank=True)),
            ],
            options={
                'ordering': ['nombre'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Departamento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=120)),
                ('slug', autoslug.fields.AutoSlugField(editable=False)),
                ('latitud', models.DecimalField(null=True, verbose_name=b'Latitud', max_digits=10, decimal_places=5, blank=True)),
                ('longitud', models.DecimalField(null=True, verbose_name=b'Longitud', max_digits=10, decimal_places=5, blank=True)),
            ],
            options={
                'ordering': ['nombre'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Municipio',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=120)),
                ('slug', autoslug.fields.AutoSlugField(editable=False)),
                ('poblacion', models.IntegerField()),
                ('latitud', models.DecimalField(null=True, verbose_name=b'Latitud', max_digits=10, decimal_places=6, blank=True)),
                ('longitud', models.DecimalField(null=True, verbose_name=b'Longitud', max_digits=10, decimal_places=6, blank=True)),
                ('depto', models.ForeignKey(related_name='departamento', to='lugar.Departamento')),
            ],
            options={
                'ordering': ['nombre'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='comarca',
            name='municipio',
            field=smart_selects.db_fields.ChainedForeignKey(chained_model_field=b'nombre', chained_field=b'departamento', blank=True, to='lugar.Municipio', null=True),
            preserve_default=True,
        ),
    ]
