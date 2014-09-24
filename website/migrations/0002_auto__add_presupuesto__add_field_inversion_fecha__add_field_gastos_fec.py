# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Presupuesto'
        db.create_table(u'website_presupuesto', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('municipio', self.gf('django.db.models.fields.related.ForeignKey')(related_name='municipio_presupuesto', to=orm['website.Municipio'])),
            ('monto', self.gf('django.db.models.fields.IntegerField')()),
            ('fecha', self.gf('django.db.models.fields.DateField')()),
            ('descripcon', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'website', ['Presupuesto'])

        # Adding field 'Inversion.fecha'
        db.add_column(u'website_inversion', 'fecha',
                      self.gf('django.db.models.fields.DateField')(null=True),
                      keep_default=False)

        # Adding field 'Gastos.fecha'
        db.add_column(u'website_gastos', 'fecha',
                      self.gf('django.db.models.fields.DateField')(null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Presupuesto'
        db.delete_table(u'website_presupuesto')

        # Deleting field 'Inversion.fecha'
        db.delete_column(u'website_inversion', 'fecha')

        # Deleting field 'Gastos.fecha'
        db.delete_column(u'website_gastos', 'fecha')


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
            'fecha': ('django.db.models.fields.DateField', [], {'null': 'True'}),
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
            'fecha': ('django.db.models.fields.DateField', [], {'null': 'True'}),
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
        u'website.presupuesto': {
            'Meta': {'object_name': 'Presupuesto'},
            'descripcon': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'fecha': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'monto': ('django.db.models.fields.IntegerField', [], {}),
            'municipio': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'municipio_presupuesto'", 'to': u"orm['website.Municipio']"})
        },
        u'website.tipogastos': {
            'Meta': {'object_name': 'TipoGastos'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['website']