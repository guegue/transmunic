# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CategoriaInversion'
        db.create_table(u'website_categoriainversion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'website', ['CategoriaInversion'])

        # Adding model 'OrigenRecursos'
        db.create_table(u'website_origenrecursos', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'website', ['OrigenRecursos'])

        # Adding model 'FuenteFmto'
        db.create_table(u'website_fuentefmto', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('origen_recurso', self.gf('django.db.models.fields.related.ForeignKey')(related_name='origen', to=orm['website.OrigenRecursos'])),
        ))
        db.send_create_signal(u'website', ['FuenteFmto'])

        # Adding model 'Municipio'
        db.create_table(u'website_municipio', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('poblacion', self.gf('django.db.models.fields.IntegerField')()),
            ('latitud', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=5, blank=True)),
            ('longitud', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=5, blank=True)),
        ))
        db.send_create_signal(u'website', ['Municipio'])

        # Adding model 'Ingresos'
        db.create_table(u'website_ingresos', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('municipio', self.gf('django.db.models.fields.related.ForeignKey')(related_name='municipio_ingreso', to=orm['website.Municipio'])),
            ('financiamiento', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fmto_ingreso', to=orm['website.FuenteFmto'])),
        ))
        db.send_create_signal(u'website', ['Ingresos'])

        # Adding model 'Area'
        db.create_table(u'website_area', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'website', ['Area'])

        # Adding model 'TipoGastos'
        db.create_table(u'website_tipogastos', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'website', ['TipoGastos'])

        # Adding model 'Gastos'
        db.create_table(u'website_gastos', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('municipio', self.gf('django.db.models.fields.related.ForeignKey')(related_name='municipio_gasto', to=orm['website.Municipio'])),
            ('area', self.gf('django.db.models.fields.related.ForeignKey')(related_name='area_gasto', to=orm['website.Area'])),
            ('financiamieno', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fmto_gasto', to=orm['website.FuenteFmto'])),
            ('tipo_gasto', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tipo_gasto', to=orm['website.TipoGastos'])),
        ))
        db.send_create_signal(u'website', ['Gastos'])

        # Adding model 'Inversion'
        db.create_table(u'website_inversion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('municipio', self.gf('django.db.models.fields.related.ForeignKey')(related_name='municipio_inversion', to=orm['website.Municipio'])),
            ('area', self.gf('django.db.models.fields.related.ForeignKey')(related_name='area_inversion', to=orm['website.Area'])),
            ('categoria_inv', self.gf('django.db.models.fields.related.ForeignKey')(related_name='categoria', to=orm['website.CategoriaInversion'])),
            ('financiamiento', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fmto_inv', to=orm['website.FuenteFmto'])),
        ))
        db.send_create_signal(u'website', ['Inversion'])


    def backwards(self, orm):
        # Deleting model 'CategoriaInversion'
        db.delete_table(u'website_categoriainversion')

        # Deleting model 'OrigenRecursos'
        db.delete_table(u'website_origenrecursos')

        # Deleting model 'FuenteFmto'
        db.delete_table(u'website_fuentefmto')

        # Deleting model 'Municipio'
        db.delete_table(u'website_municipio')

        # Deleting model 'Ingresos'
        db.delete_table(u'website_ingresos')

        # Deleting model 'Area'
        db.delete_table(u'website_area')

        # Deleting model 'TipoGastos'
        db.delete_table(u'website_tipogastos')

        # Deleting model 'Gastos'
        db.delete_table(u'website_gastos')

        # Deleting model 'Inversion'
        db.delete_table(u'website_inversion')


    models = {
        u'website.area': {
            'Meta': {'object_name': 'Area'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'website.categoriainversion': {
            'Meta': {'object_name': 'CategoriaInversion'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'website.fuentefmto': {
            'Meta': {'object_name': 'FuenteFmto'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'origen_recurso': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'origen'", 'to': u"orm['website.OrigenRecursos']"})
        },
        u'website.gastos': {
            'Meta': {'object_name': 'Gastos'},
            'area': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'area_gasto'", 'to': u"orm['website.Area']"}),
            'financiamieno': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fmto_gasto'", 'to': u"orm['website.FuenteFmto']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'municipio': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'municipio_gasto'", 'to': u"orm['website.Municipio']"}),
            'tipo_gasto': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tipo_gasto'", 'to': u"orm['website.TipoGastos']"})
        },
        u'website.ingresos': {
            'Meta': {'object_name': 'Ingresos'},
            'financiamiento': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fmto_ingreso'", 'to': u"orm['website.FuenteFmto']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'municipio': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'municipio_ingreso'", 'to': u"orm['website.Municipio']"})
        },
        u'website.inversion': {
            'Meta': {'object_name': 'Inversion'},
            'area': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'area_inversion'", 'to': u"orm['website.Area']"}),
            'categoria_inv': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'categoria'", 'to': u"orm['website.CategoriaInversion']"}),
            'financiamiento': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fmto_inv'", 'to': u"orm['website.FuenteFmto']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'municipio': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'municipio_inversion'", 'to': u"orm['website.Municipio']"})
        },
        u'website.municipio': {
            'Meta': {'object_name': 'Municipio'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitud': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '5', 'blank': 'True'}),
            'longitud': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '5', 'blank': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'poblacion': ('django.db.models.fields.IntegerField', [], {})
        },
        u'website.origenrecursos': {
            'Meta': {'object_name': 'OrigenRecursos'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'website.tipogastos': {
            'Meta': {'object_name': 'TipoGastos'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['website']