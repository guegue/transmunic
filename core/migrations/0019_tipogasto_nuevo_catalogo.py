# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-02-11 15:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_tipoingreso_ingreso_propio'),
    ]

    operations = [
        migrations.AddField(
            model_name='tipogasto',
            name='nuevo_catalogo',
            field=models.BooleanField(default=False),
        ),
    ]