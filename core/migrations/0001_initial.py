# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lugar', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AreaGeografica',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=50)),
                ('slug', models.SlugField(max_length=30)),
            ],
            options={
                'verbose_name_plural': 'Area geografica',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CatInversion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=200)),
                ('slug', models.SlugField(max_length=80)),
            ],
            options={
                'ordering': ['nombre'],
                'verbose_name_plural': 'Categorias de inversion',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Donante',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=200)),
                ('descripcion', models.CharField(max_length=500, null=True, blank=True)),
                ('enlace', models.CharField(max_length=200, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FuenteFmto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=250)),
                ('slug', models.SlugField(max_length=80)),
            ],
            options={
                'ordering': ['nombre'],
                'verbose_name_plural': 'Fuentes de financiamiento',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Gasto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tipo', models.IntegerField(default=0, choices=[(0, b'Gasto'), (1, b'Inversion')])),
                ('anio', models.IntegerField(null=True)),
                ('descripcion', models.TextField(null=True, blank=True)),
                ('areageografica', models.ForeignKey(to='core.AreaGeografica')),
                ('catinversion', models.ForeignKey(to='core.CatInversion')),
                ('comarca', models.ForeignKey(to='lugar.Comarca')),
                ('municipio', models.ForeignKey(to='lugar.Municipio')),
            ],
            options={
                'ordering': ['anio'],
                'verbose_name_plural': 'Gastos/Inversion',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GastoDetalle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fecha', models.DateField(null=True)),
                ('monto', models.DecimalField(null=True, max_digits=12, decimal_places=6, blank=True)),
                ('ejecutado', models.DecimalField(max_digits=12, decimal_places=6)),
                ('gasto', models.ForeignKey(to='core.Gasto')),
            ],
            options={
                'ordering': ['fecha'],
                'verbose_name_plural': 'Detalle de gastos/Inversion',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GastoFuenteFmto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fuentefmto', models.ForeignKey(to='core.FuenteFmto')),
                ('gasto', models.ForeignKey(to='core.Gasto')),
            ],
            options={
                'verbose_name_plural': 'Gastos - Fuentes de financiamiento',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Ingreso',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('anio', models.IntegerField()),
                ('descripcion', models.TextField(null=True, blank=True)),
                ('municipio', models.ForeignKey(to='lugar.Municipio')),
            ],
            options={
                'verbose_name_plural': 'Ingresos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IngresoDetalle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fecha', models.DateField()),
                ('monto', models.DecimalField(max_digits=12, decimal_places=6)),
                ('ejecutado', models.DecimalField(max_digits=12, decimal_places=6)),
                ('donante', models.ForeignKey(to='core.Donante')),
                ('ingreso', models.ForeignKey(to='core.Ingreso')),
            ],
            options={
                'verbose_name_plural': 'Detalle de Ingresos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrigenRecurso',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=200)),
                ('slug', models.SlugField(max_length=80)),
            ],
            options={
                'ordering': ['nombre'],
                'verbose_name_plural': 'Origen  de los recursos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Proyecto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('codigo', models.CharField(max_length=20)),
                ('nombre', models.CharField(max_length=200)),
                ('fecha_ini', models.DateField(null=True)),
                ('fecha_fin', models.DateField(null=True)),
                ('fisico', models.CharField(max_length=80)),
                ('um', models.IntegerField(default=0, verbose_name=b'U.M', choices=[(0, b'm2'), (1, b'Km'), (2, b'Mz'), (3, b'Unidad')])),
                ('descripcion', models.TextField(null=True, blank=True)),
                ('areageografica', models.ForeignKey(related_name='area_geografica', to='core.AreaGeografica')),
                ('catinversion', models.ForeignKey(related_name='categoria_inversion', to='core.CatInversion')),
                ('comarca', models.ForeignKey(to='lugar.Comarca')),
                ('municipio', models.ForeignKey(related_name='nombre_municipio', to='lugar.Municipio')),
            ],
            options={
                'verbose_name_plural': 'Proyectos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProyectoDetalle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('financiamiento', models.DecimalField(max_digits=12, decimal_places=6)),
                ('fecha', models.DateField(null=True)),
                ('proyecto', models.ForeignKey(to='core.Proyecto')),
            ],
            options={
                'verbose_name_plural': 'Proyecto detalle',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubSubTipoIngreso',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=250)),
                ('slug', models.SlugField(max_length=80)),
            ],
            options={
                'ordering': ['nombre'],
                'verbose_name_plural': 'Sub-subtipos de ingresos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubTipoGasto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=200)),
                ('slug', models.SlugField(max_length=80)),
            ],
            options={
                'ordering': ['nombre'],
                'verbose_name_plural': 'Sub-Tipo de gastos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubTipoIngreso',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=250)),
                ('slug', models.SlugField(max_length=80)),
            ],
            options={
                'ordering': ['nombre'],
                'verbose_name_plural': 'Subtipos de ingresos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TipoGasto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=200)),
                ('slug', models.SlugField(max_length=80)),
            ],
            options={
                'ordering': ['nombre'],
                'verbose_name_plural': 'Tipo de gastos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TipoIngreso',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=200)),
                ('slug', models.SlugField()),
                ('clasificacion', models.IntegerField(default=0, choices=[(0, b'Ingreso Corriente'), (1, b'Ingreso Capital')])),
            ],
            options={
                'ordering': ['nombre'],
                'verbose_name_plural': 'Tipo de ingreso',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TipoProyecto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=200)),
                ('slug', models.SlugField(max_length=80)),
            ],
            options={
                'ordering': ['nombre'],
                'verbose_name_plural': 'Tipo de proyectos',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='subtipoingreso',
            name='tipoingreso',
            field=models.ForeignKey(related_name='tipo', to='core.TipoIngreso'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='subtipogasto',
            name='tipogasto',
            field=models.ForeignKey(related_name='tipo', to='core.TipoGasto'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='subsubtipoingreso',
            name='subtipoingreso',
            field=models.ForeignKey(related_name='tipo', to='core.SubTipoIngreso'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='proyecto',
            name='tipoproyecto',
            field=models.ForeignKey(related_name='tipo_proyecto', to='core.TipoProyecto'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ingreso',
            name='subsubtipoingreso',
            field=models.ForeignKey(to='core.SubSubTipoIngreso'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gasto',
            name='origen',
            field=models.ForeignKey(to='core.SubSubTipoIngreso'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gasto',
            name='subtipogasto',
            field=models.ForeignKey(to='core.TipoGasto'),
            preserve_default=True,
        ),
    ]
