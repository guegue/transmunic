# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields
import pixelfields_smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('lugar', '0011_remove_poblacion_departamento'),
        ('core', '0003_subsubtipogasto_origen'),
    ]

    operations = [
        migrations.CreateModel(
            name='InversionFuente',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fecha', models.DateField()),
                ('departamento', models.ForeignKey(to='lugar.Departamento')),
                ('municipio', pixelfields_smart_selects.db_fields.ChainedForeignKey(blank=True, to='lugar.Municipio', null=True)),
            ],
            options={
                'verbose_name_plural': 'Inversion de fuentes de financiamiento',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InversionFuenteDetalle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('asignado', models.DecimalField(null=True, max_digits=12, decimal_places=2, blank=True)),
                ('ejecutado', models.DecimalField(max_digits=12, decimal_places=2)),
                ('fuente', models.ForeignKey(to='core.FuenteFmto')),
                ('inversionfuente', models.ForeignKey(to='core.InversionFuente')),
            ],
            options={
                'ordering': ['inversionfuente'],
                'verbose_name_plural': 'Detalle de inversion por fuente',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TipoFuenteFmto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=250)),
                ('slug', autoslug.fields.AutoSlugField(editable=False)),
            ],
            options={
                'ordering': ['nombre'],
                'verbose_name_plural': 'Tipos de Fuentes de financiamiento',
            },
            bases=(models.Model,),
        ),
        migrations.DeleteModel(
            name='Donante',
        ),
        migrations.AddField(
            model_name='inversionfuentedetalle',
            name='tipofuente',
            field=models.ForeignKey(to='core.TipoFuenteFmto'),
            preserve_default=True,
        ),
    ]
