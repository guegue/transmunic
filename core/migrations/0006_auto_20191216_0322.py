# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2019-12-16 09:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20191216_0321'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sub3tipoingreso',
            name='subsubtipoingreso',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subsubtipo', to='core.SubSubTipoIngreso'),
        ),
    ]
