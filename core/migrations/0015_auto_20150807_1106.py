# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20150622_1052'),
    ]

    operations = [
        migrations.CreateModel(
            name='grafico',
            fields=[
                ('id', models.CharField(max_length=25, serialize=False, primary_key=True)),
                ('nombre', models.CharField(max_length=200)),
                ('descripcion', models.TextField(null=True, blank=True)),
                ('notas', models.TextField(null=True, blank=True)),
                ('imagen_objetivo', sorl.thumbnail.fields.ImageField(null=True, upload_to=b'grafico', blank=True)),
                ('imagen_actual', sorl.thumbnail.fields.ImageField(null=True, upload_to=b'grafico', blank=True)),
            ],
            options={
                'ordering': ['nombre'],
                'verbose_name_plural': 'Graficos',
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='gasto',
            name='anio',
            field=models.IntegerField(verbose_name='A\xf1o'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ingreso',
            name='anio',
            field=models.IntegerField(verbose_name='A\xf1o'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='inversion',
            name='anio',
            field=models.IntegerField(verbose_name='A\xf1o'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='inversion',
            name='municipio',
            field=models.ForeignKey(blank=True, to='lugar.Municipio', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='inversionfuente',
            name='anio',
            field=models.IntegerField(verbose_name='A\xf1o'),
            preserve_default=True,
        ),
    ]
