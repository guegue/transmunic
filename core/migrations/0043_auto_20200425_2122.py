# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-04-26 03:22
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0042_subtipoingreso_origen_ic'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrigenGastosCorrientes',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200, unique=True)),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from=b'nombre')),
                ('shortname', models.CharField(blank=True, max_length=25, null=True)),
                ('orden', models.IntegerField()),
            ],
            options={
                'ordering': ['orden', 'nombre'],
                'verbose_name': 'Origen de Gasto Corriente',
                'verbose_name_plural': 'Origen de Gastos Corrientes',
            },
        ),
        migrations.AddField(
            model_name='subsubtipogasto',
            name='origen_gc',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.
                                    models.deletion.CASCADE,
                                    to='core.OrigenGastosCorrientes',
                                    verbose_name=b'Origen Gasto de Corriente'),
        ),
    ]
