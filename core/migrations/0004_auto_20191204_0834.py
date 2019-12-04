# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2019-12-04 14:34
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations
import django.db.models.deletion
import pixelfields_smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20191122_0130'),
    ]

    operations = [
        migrations.AddField(
            model_name='anio',
            name='mapping',
            field=django.contrib.postgres.fields.jsonb.JSONField(default='{}'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='gasto',
            name='municipio',
            field=pixelfields_smart_selects.db_fields.ChainedForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='lugar.Municipio'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='ingreso',
            name='municipio',
            field=pixelfields_smart_selects.db_fields.ChainedForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='lugar.Municipio'),
            preserve_default=False,
        ),
    ]
