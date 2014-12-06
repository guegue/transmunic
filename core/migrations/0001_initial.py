# -*- coding: utf-8 -*-
<<<<<<< HEAD
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
=======
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Ingreso'
        db.create_table(u'core_ingreso', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('anio', self.gf('django.db.models.fields.IntegerField')()),
            ('municipio', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Municipio'])),
            ('subsubtipoingreso', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.SubSubTipoIngreso'])),
            ('descripcion', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['Ingreso'])

        # Adding model 'IngresoDetalle'
        db.create_table(u'core_ingresodetalle', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ingreso', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Ingreso'])),
            ('fecha', self.gf('django.db.models.fields.DateField')()),
            ('monto', self.gf('django.db.models.fields.DecimalField')(max_digits=12, decimal_places=6)),
            ('ejecutado', self.gf('django.db.models.fields.DecimalField')(max_digits=12, decimal_places=6)),
            ('donante', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Donante'])),
        ))
        db.send_create_signal(u'core', ['IngresoDetalle'])

        # Adding model 'Gasto'
        db.create_table(u'core_gasto', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tipo', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('fecha', self.gf('django.db.models.fields.DateField')(null=True)),
            ('origen', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.SubSubTipoIngreso'])),
            ('monto', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=6, blank=True)),
            ('municipio', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Municipio'])),
            ('comarca', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Comarca'])),
            ('subtipogasto', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.TipoGasto'])),
            ('catinversion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.CatInversion'])),
            ('areageografica', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.AreaGeografica'])),
            ('descripcion', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['Gasto'])

        # Adding model 'GastoFuenteFmto'
        db.create_table(u'core_gastofuentefmto', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('gasto', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Gasto'])),
            ('fuentefmto', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.FuenteFmto'])),
        ))
        db.send_create_signal(u'core', ['GastoFuenteFmto'])

        # Adding model 'Proyecto'
        db.create_table(u'core_proyecto', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('municipio', self.gf('django.db.models.fields.related.ForeignKey')(related_name='nombre_municipio', to=orm['website.Municipio'])),
            ('comarca', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Comarca'])),
            ('codigo', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('fecha_ini', self.gf('django.db.models.fields.DateField')(null=True)),
            ('fecha_fin', self.gf('django.db.models.fields.DateField')(null=True)),
            ('tipoproyecto', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tipo_proyecto', to=orm['website.TipoProyecto'])),
            ('catinversion', self.gf('django.db.models.fields.related.ForeignKey')(related_name='categoria_inversion', to=orm['website.CatInversion'])),
            ('areageografica', self.gf('django.db.models.fields.related.ForeignKey')(related_name='area_geografica', to=orm['website.AreaGeografica'])),
            ('fisico', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('um', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('descripcion', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['Proyecto'])

        # Adding model 'ProyectoDetalle'
        db.create_table(u'core_proyectodetalle', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('proyecto', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Proyecto'])),
            ('financiamiento', self.gf('django.db.models.fields.DecimalField')(max_digits=12, decimal_places=6)),
            ('fecha', self.gf('django.db.models.fields.DateField')(null=True)),
        ))
        db.send_create_signal(u'core', ['ProyectoDetalle'])


    def backwards(self, orm):
        # Deleting model 'Ingreso'
        db.delete_table(u'core_ingreso')

        # Deleting model 'IngresoDetalle'
        db.delete_table(u'core_ingresodetalle')

        # Deleting model 'Gasto'
        db.delete_table(u'core_gasto')

        # Deleting model 'GastoFuenteFmto'
        db.delete_table(u'core_gastofuentefmto')

        # Deleting model 'Proyecto'
        db.delete_table(u'core_proyecto')

        # Deleting model 'ProyectoDetalle'
        db.delete_table(u'core_proyectodetalle')


    models = {
        u'core.gasto': {
            'Meta': {'ordering': "['fecha']", 'object_name': 'Gasto'},
            'areageografica': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['website.AreaGeografica']"}),
            'catinversion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['website.CatInversion']"}),
            'comarca': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['website.Comarca']"}),
            'descripcion': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'fecha': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'monto': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '6', 'blank': 'True'}),
            'municipio': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['website.Municipio']"}),
            'origen': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['website.SubSubTipoIngreso']"}),
            'subtipogasto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['website.TipoGasto']"}),
            'tipo': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'core.gastofuentefmto': {
            'Meta': {'object_name': 'GastoFuenteFmto'},
            'fuentefmto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['website.FuenteFmto']"}),
            'gasto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Gasto']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'core.ingreso': {
            'Meta': {'object_name': 'Ingreso'},
            'anio': ('django.db.models.fields.IntegerField', [], {}),
            'descripcion': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'municipio': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['website.Municipio']"}),
            'subsubtipoingreso': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['website.SubSubTipoIngreso']"})
        },
        u'core.ingresodetalle': {
            'Meta': {'object_name': 'IngresoDetalle'},
            'donante': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['website.Donante']"}),
            'ejecutado': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '6'}),
            'fecha': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ingreso': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Ingreso']"}),
            'monto': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '6'})
        },
        u'core.proyecto': {
            'Meta': {'object_name': 'Proyecto'},
            'areageografica': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'area_geografica'", 'to': u"orm['website.AreaGeografica']"}),
            'catinversion': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'categoria_inversion'", 'to': u"orm['website.CatInversion']"}),
            'codigo': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'comarca': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['website.Comarca']"}),
            'descripcion': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'fecha_fin': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'fecha_ini': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'fisico': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'municipio': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'nombre_municipio'", 'to': u"orm['website.Municipio']"}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'tipoproyecto': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tipo_proyecto'", 'to': u"orm['website.TipoProyecto']"}),
            'um': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'core.proyectodetalle': {
            'Meta': {'object_name': 'ProyectoDetalle'},
            'fecha': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'financiamiento': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '6'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'proyecto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Proyecto']"})
        },
        u'website.areageografica': {
            'Meta': {'object_name': 'AreaGeografica'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '30'})
        },
        u'website.catinversion': {
            'Meta': {'ordering': "['nombre']", 'object_name': 'CatInversion'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '80'})
        },
        u'website.comarca': {
            'Meta': {'ordering': "['nombre']", 'object_name': 'Comarca'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitud': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '6', 'blank': 'True'}),
            'longitud': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '6', 'blank': 'True'}),
            'municipio': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['website.Municipio']"}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'poblacion': ('django.db.models.fields.IntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '60'})
        },
        u'website.departamento': {
            'Meta': {'ordering': "['nombre']", 'object_name': 'Departamento'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitud': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '5', 'blank': 'True'}),
            'longitud': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '5', 'blank': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '60'})
        },
        u'website.donante': {
            'Meta': {'object_name': 'Donante'},
            'descripcion': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'enlace': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'website.fuentefmto': {
            'Meta': {'ordering': "['nombre']", 'object_name': 'FuenteFmto'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '80'})
        },
        u'website.municipio': {
            'Meta': {'ordering': "['nombre']", 'object_name': 'Municipio'},
            'depto': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'departamento'", 'to': u"orm['website.Departamento']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitud': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '6', 'blank': 'True'}),
            'longitud': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '6', 'blank': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'poblacion': ('django.db.models.fields.IntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '60'})
        },
        u'website.subsubtipoingreso': {
            'Meta': {'ordering': "['nombre']", 'object_name': 'SubSubTipoIngreso'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '80'}),
            'subtipoingreso': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tipo'", 'to': u"orm['website.SubTipoIngreso']"})
        },
        u'website.subtipoingreso': {
            'Meta': {'ordering': "['nombre']", 'object_name': 'SubTipoIngreso'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '80'}),
            'tipoingreso': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tipo'", 'to': u"orm['website.TipoIngreso']"})
        },
        u'website.tipogasto': {
            'Meta': {'ordering': "['nombre']", 'object_name': 'TipoGasto'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '80'})
        },
        u'website.tipoingreso': {
            'Meta': {'ordering': "['nombre']", 'object_name': 'TipoIngreso'},
            'clasificacion': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        u'website.tipoproyecto': {
            'Meta': {'ordering': "['nombre']", 'object_name': 'TipoProyecto'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '80'})
        }
    }

    complete_apps = ['core']
>>>>>>> 618bbfa7c906fa39fcb1bbf395482db81f72aad5
