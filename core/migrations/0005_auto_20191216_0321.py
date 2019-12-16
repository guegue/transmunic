# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2019-12-16 09:21
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20191204_0834'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sub3TipoIngreso',
            fields=[
                ('codigo', models.CharField(max_length=25, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=200)),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from=b'nombre')),
                ('shortname', models.CharField(blank=True, max_length=25, null=True)),
                ('subsubtipoingreso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                                        related_name='subsubtipo', to='core.SubTipoIngreso')),
            ],
            options={
                'ordering': ['codigo'],
                'verbose_name': 'Sub3 Tipo de ingreso',
                'verbose_name_plural': 'Sub3 Tipo de ingreso',
            },
        ),
        migrations.AlterField(
            model_name='ingresorenglon',
            name='subsubtipoingreso',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.SubSubTipoIngreso'),
        ),
        migrations.AddField(
            model_name='ingresorenglon',
            name='sub3tipoingreso',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Sub3TipoIngreso'),
        ),
    ]
