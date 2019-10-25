# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields
import sorl.thumbnail.fields
import pixelfields_smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('lugar', '0019_auto_20151203_1405'),
    ]

    operations = [
        migrations.CreateModel(
            name='Anio',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('anio', models.IntegerField()),
                ('periodo', models.CharField(max_length=1)),
                ('inicial', models.DateField(null=True, blank=True)),
                ('actualizado', models.DateField(null=True, blank=True)),
                ('final', models.DateField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CatInversion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=200)),
                ('slug', models.SlugField(max_length=80)),
                ('minimo', models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)),
                ('destacar', models.BooleanField(default=False)),
                ('color', models.CharField(default=b'#2b7ab3', max_length=8)),
                ('shortname', models.CharField(max_length=25, null=True, blank=True)),
            ],
            options={
                'ordering': ['nombre'],
                'verbose_name': 'Categoria de inversion',
                'verbose_name_plural': 'Categorias de inversion',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FuenteFmto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=250)),
                ('slug', autoslug.fields.AutoSlugField(editable=False)),
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
                ('fecha', models.DateField()),
                ('anio', models.IntegerField(verbose_name='A\xf1o')),
                ('periodo', models.CharField(max_length=1)),
                ('descripcion', models.TextField(null=True, blank=True)),
                ('departamento', models.ForeignKey(to='lugar.Departamento')),
                ('municipio', pixelfields_smart_selects.db_fields.ChainedForeignKey(blank=True, to='lugar.Municipio', null=True)),
            ],
            options={
                'ordering': ['fecha'],
                'verbose_name_plural': 'Gastos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GastoDetalle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('codigo', models.CharField(max_length=15)),
                ('cuenta', models.CharField(max_length=400)),
                ('asignado', models.DecimalField(null=True, max_digits=12, decimal_places=2, blank=True)),
                ('ejecutado', models.DecimalField(max_digits=12, decimal_places=2)),
                ('gasto', models.ForeignKey(to='core.Gasto')),
            ],
            options={
                'ordering': ['gasto'],
                'verbose_name_plural': 'Detalle de gastos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Grafico',
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
        migrations.CreateModel(
            name='Ingreso',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fecha', models.DateField()),
                ('anio', models.IntegerField(verbose_name='A\xf1o')),
                ('periodo', models.CharField(max_length=1)),
                ('descripcion', models.TextField(null=True, blank=True)),
                ('departamento', models.ForeignKey(to='lugar.Departamento')),
                ('municipio', pixelfields_smart_selects.db_fields.ChainedForeignKey(blank=True, to='lugar.Municipio', null=True)),
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
                ('codigo', models.CharField(max_length=15)),
                ('cuenta', models.CharField(max_length=400)),
                ('asignado', models.DecimalField(null=True, max_digits=12, decimal_places=2, blank=True)),
                ('ejecutado', models.DecimalField(max_digits=12, decimal_places=2)),
                ('ingreso', models.ForeignKey(to='core.Ingreso')),
            ],
            options={
                'ordering': ['ingreso'],
                'verbose_name_plural': 'Detalle de ingresos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Inversion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombremunic', models.CharField(max_length=250, null=True, blank=True)),
                ('fecha', models.DateField()),
                ('anio', models.IntegerField(verbose_name='A\xf1o')),
                ('periodo', models.CharField(max_length=1)),
                ('departamento', models.ForeignKey(to='lugar.Departamento', null=True)),
                ('municipio', models.ForeignKey(blank=True, to='lugar.Municipio', null=True)),
            ],
            options={
                'verbose_name_plural': 'Inversion',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InversionFuente',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fecha', models.DateField()),
                ('anio', models.IntegerField(verbose_name='A\xf1o')),
                ('periodo', models.CharField(max_length=1)),
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
                ('fuente', pixelfields_smart_selects.db_fields.ChainedForeignKey(blank=True, to='core.FuenteFmto', null=True)),
                ('inversionfuente', models.ForeignKey(to='core.InversionFuente')),
            ],
            options={
                'ordering': ['inversionfuente'],
                'verbose_name_plural': 'Detalle de inversion por fuente',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Organizacion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=200)),
                ('descripcion', models.TextField(null=True, blank=True)),
                ('correo', models.CharField(max_length=100, null=True, blank=True)),
                ('web', models.CharField(max_length=200, null=True, blank=True)),
                ('logo', sorl.thumbnail.fields.ImageField(null=True, upload_to=b'organizacion', blank=True)),
            ],
            options={
                'ordering': ['nombre'],
                'verbose_name_plural': 'Organizaciones',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrigenGasto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=200)),
                ('slug', autoslug.fields.AutoSlugField(editable=False)),
                ('shortname', models.CharField(max_length=25, null=True, blank=True)),
            ],
            options={
                'ordering': ['nombre'],
                'verbose_name_plural': 'Origen  de los gastos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrigenRecurso',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=200)),
                ('slug', autoslug.fields.AutoSlugField(editable=False)),
                ('shortname', models.CharField(max_length=25, null=True, blank=True)),
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
                ('codigo', models.CharField(max_length=20, null=True)),
                ('nombre', models.CharField(max_length=500)),
                ('areageografica', models.CharField(blank=True, max_length=1, null=True, choices=[(b'U', b'Urbana'), (b'R', b'Rural'), (b'O', b'Otros')])),
                ('asignado', models.DecimalField(null=True, max_digits=12, decimal_places=2, blank=True)),
                ('ejecutado', models.DecimalField(max_digits=12, decimal_places=2)),
                ('ficha', models.FileField(null=True, upload_to=b'proyecto', blank=True)),
                ('catinversion', models.ForeignKey(related_name='categoria_inversion', verbose_name='Categor\xeda de Inversi\xf3n', blank=True, to='core.CatInversion', null=True)),
                ('inversion', models.ForeignKey(related_name='inversion', to='core.Inversion', null=True)),
            ],
            options={
                'verbose_name_plural': 'Proyectos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubSubTipoGasto',
            fields=[
                ('codigo', models.CharField(max_length=25, serialize=False, primary_key=True)),
                ('nombre', models.CharField(max_length=200)),
                ('slug', autoslug.fields.AutoSlugField(editable=False)),
                ('shortname', models.CharField(max_length=25, null=True, blank=True)),
                ('origen', models.ForeignKey(related_name='origen', to='core.OrigenGasto', null=True)),
            ],
            options={
                'ordering': ['nombre'],
                'verbose_name_plural': 'Sub-Sub-Tipo de gastos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubSubTipoIngreso',
            fields=[
                ('codigo', models.CharField(max_length=25, serialize=False, primary_key=True)),
                ('nombre', models.CharField(max_length=200)),
                ('slug', autoslug.fields.AutoSlugField(editable=False)),
                ('shortname', models.CharField(max_length=25, null=True, blank=True)),
                ('origen', models.ForeignKey(related_name='origen', to='core.OrigenRecurso', null=True)),
            ],
            options={
                'ordering': ['codigo'],
                'verbose_name_plural': 'Sub-subtipos de ingresos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubTipoGasto',
            fields=[
                ('codigo', models.CharField(max_length=25, serialize=False, primary_key=True)),
                ('nombre', models.CharField(max_length=200)),
                ('slug', autoslug.fields.AutoSlugField(editable=False)),
                ('shortname', models.CharField(max_length=25, null=True, blank=True)),
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
                ('codigo', models.CharField(max_length=25, serialize=False, primary_key=True)),
                ('nombre', models.CharField(max_length=200)),
                ('slug', autoslug.fields.AutoSlugField(editable=False)),
                ('shortname', models.CharField(max_length=25, null=True, blank=True)),
            ],
            options={
                'ordering': ['codigo'],
                'verbose_name_plural': 'Subtipos de ingresos',
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
        migrations.CreateModel(
            name='TipoGasto',
            fields=[
                ('codigo', models.CharField(max_length=25, serialize=False, primary_key=True)),
                ('nombre', models.CharField(max_length=200)),
                ('slug', autoslug.fields.AutoSlugField(null=True, editable=False)),
                ('shortname', models.CharField(max_length=25, null=True, blank=True)),
                ('clasificacion', models.IntegerField(default=0, null=True, choices=[(b'0', b'Gasto Corriente'), (b'1', b'Gasto de Capital')])),
            ],
            options={
                'ordering': ['codigo'],
                'verbose_name_plural': 'Tipo de gastos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TipoIngreso',
            fields=[
                ('codigo', models.CharField(max_length=25, serialize=False, primary_key=True)),
                ('nombre', models.CharField(max_length=200)),
                ('slug', autoslug.fields.AutoSlugField(null=True, editable=False)),
                ('shortname', models.CharField(max_length=25, null=True, blank=True)),
                ('clasificacion', models.IntegerField(default=0, null=True, choices=[(0, b'Ingreso Corriente'), (1, b'Ingreso Capital')])),
            ],
            options={
                'ordering': ['codigo'],
                'verbose_name_plural': 'Tipo de ingreso',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TipoProyecto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=200)),
                ('slug', autoslug.fields.AutoSlugField(editable=False)),
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
            field=models.ForeignKey(related_name='subtipo', to='core.SubTipoIngreso'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='subsubtipogasto',
            name='subtipogasto',
            field=models.ForeignKey(related_name='subtipo', to='core.SubTipoGasto'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='proyecto',
            name='tipoproyecto',
            field=models.ForeignKey(related_name='tipo_proyecto', blank=True, to='core.TipoProyecto', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='inversionfuentedetalle',
            name='tipofuente',
            field=models.ForeignKey(to='core.TipoFuenteFmto'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ingresodetalle',
            name='subsubtipoingreso',
            field=pixelfields_smart_selects.db_fields.ChainedForeignKey(blank=True, to='core.SubSubTipoIngreso', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ingresodetalle',
            name='subtipoingreso',
            field=pixelfields_smart_selects.db_fields.ChainedForeignKey(blank=True, to='core.SubTipoIngreso', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ingresodetalle',
            name='tipoingreso',
            field=models.ForeignKey(to='core.TipoIngreso'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gastodetalle',
            name='subsubtipogasto',
            field=pixelfields_smart_selects.db_fields.ChainedForeignKey(blank=True, to='core.SubSubTipoGasto', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gastodetalle',
            name='subtipogasto',
            field=pixelfields_smart_selects.db_fields.ChainedForeignKey(blank=True, to='core.SubTipoGasto', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gastodetalle',
            name='tipogasto',
            field=models.ForeignKey(to='core.TipoGasto'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='fuentefmto',
            name='tipofuente',
            field=models.ForeignKey(to='core.TipoFuenteFmto'),
            preserve_default=True,
        ),
    ]
