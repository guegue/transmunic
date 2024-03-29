# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2019-11-15 04:35
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations, models
import django.db.models.deletion
import pixelfields_smart_selects.db_fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ClasificacionMunic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clasificacion', models.CharField(max_length=120)),
                ('fecha_desde', models.DateField()),
                ('fecha_hasta', models.DateField()),
                ('desde', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name=b'Desde')),
                ('hasta', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name=b'Hasta')),
                ('minimo_inversion', models.IntegerField(null=True)),
                ('color', models.CharField(max_length=30, null=True)),
            ],
            options={
                'ordering': ['clasificacion'],
            },
        ),
        migrations.CreateModel(
            name='ClasificacionMunicAno',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('anio', models.IntegerField()),
                ('clasificacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clase', to='lugar.ClasificacionMunic')),
            ],
        ),
        migrations.CreateModel(
            name='Comarca',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=120)),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from=b'nombre')),
                ('poblacion', models.IntegerField()),
                ('latitud', models.DecimalField(blank=True, decimal_places=6, max_digits=10, null=True, verbose_name=b'Latitud')),
                ('longitud', models.DecimalField(blank=True, decimal_places=6, max_digits=10, null=True, verbose_name=b'Longitud')),
            ],
            options={
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Departamento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=120, unique=True)),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from=b'nombre', unique=True)),
                ('codigo', models.CharField(blank=True, max_length=15, verbose_name=b'Codigo')),
                ('latitud', models.DecimalField(blank=True, decimal_places=5, max_digits=10, null=True, verbose_name=b'Latitud')),
                ('longitud', models.DecimalField(blank=True, decimal_places=5, max_digits=10, null=True, verbose_name=b'Longitud')),
            ],
            options={
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Municipio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=120, unique=True)),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from=b'nombre', unique=True, verbose_name=b'municipio')),
                ('latitud', models.DecimalField(blank=True, decimal_places=6, max_digits=10, null=True, verbose_name=b'Latitud')),
                ('longitud', models.DecimalField(blank=True, decimal_places=6, max_digits=10, null=True, verbose_name=b'Longitud')),
                ('clasificaciones', models.ManyToManyField(through='lugar.ClasificacionMunicAno', to='lugar.ClasificacionMunic')),
                ('depto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='departamento', to='lugar.Departamento')),
            ],
            options={
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Poblacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('anio', models.IntegerField()),
                ('poblacion', models.IntegerField()),
                ('municipio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lugar.Municipio')),
            ],
            options={
                'ordering': ['anio'],
            },
        ),
        migrations.AddField(
            model_name='comarca',
            name='departamento',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lugar.Departamento'),
        ),
        migrations.AddField(
            model_name='comarca',
            name='municipio',
            field=pixelfields_smart_selects.db_fields.ChainedForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='lugar.Municipio'),
        ),
        migrations.AddField(
            model_name='clasificacionmunicano',
            name='municipio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clase', to='lugar.Municipio'),
        ),
        migrations.AlterUniqueTogether(
            name='clasificacionmunicano',
            unique_together=set([('municipio', 'anio')]),
        ),
    ]
