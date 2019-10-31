# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lugar', '0012_auto_20150410_1220'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClasificacionMunicAno',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField()),
                ('clasificacion', models.ForeignKey(to='lugar.ClasificacionMunic')),
                ('municipio', models.ForeignKey(to='lugar.Municipio')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='municipio',
            name='clasificaciones',
            field=models.ManyToManyField(to='lugar.ClasificacionMunic', through='lugar.ClasificacionMunicAno'),
            preserve_default=True,
        ),
    ]
