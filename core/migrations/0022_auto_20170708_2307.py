# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20170708_2218'),
    ]

    operations = [
        migrations.AddField(
            model_name='origengasto',
            name='shortname',
            field=models.CharField(max_length=25, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='origenrecurso',
            name='shortname',
            field=models.CharField(max_length=25, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='subsubtipogasto',
            name='shortname',
            field=models.CharField(max_length=25, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='subsubtipoingreso',
            name='shortname',
            field=models.CharField(max_length=25, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='subtipogasto',
            name='shortname',
            field=models.CharField(max_length=25, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='subtipoingreso',
            name='shortname',
            field=models.CharField(max_length=25, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tipogasto',
            name='shortname',
            field=models.CharField(max_length=25, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tipoingreso',
            name='shortname',
            field=models.CharField(max_length=25, null=True, blank=True),
            preserve_default=True,
        ),
    ]
