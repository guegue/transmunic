# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2020-04-21 19:54
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0037_auto_20200406_1643'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrigenGastoPersonal',
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
                'verbose_name': 'Origen de los gastos de personal',
                'verbose_name_plural': 'Origen de Gasto de personal',
            },
        ),
        migrations.AddField(
            model_name='subsubtipogasto',
            name='origen_gp',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='origen_gp', to='core.OrigenGastoPersonal'),
        ),
    ]
