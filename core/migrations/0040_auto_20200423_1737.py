# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-04-23 23:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0039_auto_20200423_1611'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subtipogasto',
            name='origen_gp',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='origen_gp', to='core.OrigenGastoPersonal'),
        ),
    ]
