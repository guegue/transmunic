# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-02-18 21:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_auto_20200218_1504'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aniotransferencia',
            name='inversion_publica',
        ),
        migrations.AlterField(
            model_name='aniotransferencia',
            name='pgr',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=25, null=True),
        ),
    ]
