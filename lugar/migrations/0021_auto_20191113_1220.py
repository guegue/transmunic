# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2019-11-13 18:20
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lugar', '0020_auto_20191111_2034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='departamento',
            name='nombre',
            field=models.CharField(max_length=120, unique=True),
        ),
        migrations.AlterField(
            model_name='departamento',
            name='slug',
            field=autoslug.fields.AutoSlugField(
                editable=False, populate_from=b'nombre', unique=True),
        ),
        migrations.AlterField(
            model_name='municipio',
            name='nombre',
            field=models.CharField(max_length=120, unique=True),
        ),
        migrations.AlterField(
            model_name='municipio',
            name='slug',
            field=autoslug.fields.AutoSlugField(
                editable=False, populate_from=b'nombre', unique=True, verbose_name=b'municipio'),
        ),
    ]