# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-04-23 22:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0038_auto_20200421_1354'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subsubtipogasto',
            name='origen_gp',
        ),
        migrations.AddField(
            model_name='subtipogasto',
            name='origen_gp',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='origen_gp', to='core.OrigenGastoPersonal'),
        ),
    ]
