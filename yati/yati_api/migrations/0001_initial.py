# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Project'
        db.create_table(u'yati_api_project', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'yati_api', ['Project'])

        # Adding model 'Store'
        db.create_table(u'yati_api_store', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='po', max_length=100)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='stores', to=orm['yati_api.Project'])),
            ('source', self.gf('django.db.models.fields.TextField')(null=True)),
            ('sourcelanguage', self.gf('django.db.models.fields.CharField')(default='en', max_length=10)),
            ('targetlanguage', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('last_read', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('last_write', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'yati_api', ['Store'])

        # Adding model 'Unit'
        db.create_table(u'yati_api_unit', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('index', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('store', self.gf('django.db.models.fields.related.ForeignKey')(related_name='units', to=orm['yati_api.Store'])),
            ('msgid', self.gf('dbarray.fields.TextArrayField')(default=[], null=True)),
            ('msgstr', self.gf('dbarray.fields.TextArrayField')(default=[])),
            ('comments', self.gf('django.db.models.fields.TextField')(default='')),
        ))
        db.send_create_signal(u'yati_api', ['Unit'])

        # Adding model 'Location'
        db.create_table(u'yati_api_location', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(related_name='locations', to=orm['yati_api.Unit'])),
            ('filename', self.gf('django.db.models.fields.TextField')()),
            ('lineno', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'yati_api', ['Location'])

        # Adding model 'Module'
        db.create_table(u'yati_api_module', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='modules', to=orm['yati_api.Project'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('pattern', self.gf('django.db.models.fields.TextField')(null=True)),
        ))
        db.send_create_signal(u'yati_api', ['Module'])


    def backwards(self, orm):
        # Deleting model 'Project'
        db.delete_table(u'yati_api_project')

        # Deleting model 'Store'
        db.delete_table(u'yati_api_store')

        # Deleting model 'Unit'
        db.delete_table(u'yati_api_unit')

        # Deleting model 'Location'
        db.delete_table(u'yati_api_location')

        # Deleting model 'Module'
        db.delete_table(u'yati_api_module')


    models = {
        u'yati_api.location': {
            'Meta': {'object_name': 'Location'},
            'filename': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lineno': ('django.db.models.fields.IntegerField', [], {}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'locations'", 'to': u"orm['yati_api.Unit']"})
        },
        u'yati_api.module': {
            'Meta': {'object_name': 'Module'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pattern': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'modules'", 'to': u"orm['yati_api.Project']"})
        },
        u'yati_api.project': {
            'Meta': {'object_name': 'Project'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'yati_api.store': {
            'Meta': {'object_name': 'Store'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_read': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_write': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stores'", 'to': u"orm['yati_api.Project']"}),
            'source': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'sourcelanguage': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '10'}),
            'targetlanguage': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'po'", 'max_length': '100'})
        },
        u'yati_api.unit': {
            'Meta': {'ordering': "('store', 'index')", 'object_name': 'Unit'},
            'comments': ('django.db.models.fields.TextField', [], {'default': "''"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'msgid': ('dbarray.fields.TextArrayField', [], {'default': '[]', 'null': 'True'}),
            'msgstr': ('dbarray.fields.TextArrayField', [], {'default': '[]'}),
            'store': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'units'", 'to': u"orm['yati_api.Store']"})
        }
    }

    complete_apps = ['yati_api']