# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table(u'yati_api_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('email', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=75)),
            ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('languages', self.gf('django.db.models.fields.CharField')(default=None, max_length=255, null=True)),
        ))
        db.send_create_signal(u'yati_api', ['User'])

        # Adding M2M table for field groups on 'User'
        m2m_table_name = db.shorten_name(u'yati_api_user_groups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm[u'yati_api.user'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(m2m_table_name, ['user_id', 'group_id'])

        # Adding M2M table for field user_permissions on 'User'
        m2m_table_name = db.shorten_name(u'yati_api_user_user_permissions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm[u'yati_api.user'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(m2m_table_name, ['user_id', 'permission_id'])

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
            ('filename', self.gf('django.db.models.fields.TextField')()),
            ('sourcelanguage', self.gf('django.db.models.fields.CharField')(default='en', max_length=10)),
            ('targetlanguage', self.gf('django.db.models.fields.CharField')(max_length=10)),
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
            ('fuzzy', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('obsolete', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'yati_api', ['Unit'])

        # Adding model 'StoreLog'
        db.create_table(u'yati_api_storelog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('data', self.gf('django.db.models.fields.TextField')(null=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yati_api.User'], null=True)),
            ('store', self.gf('django.db.models.fields.related.ForeignKey')(related_name='logs', to=orm['yati_api.Store'])),
            ('event', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'yati_api', ['StoreLog'])

        # Adding model 'UnitLog'
        db.create_table(u'yati_api_unitlog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('data', self.gf('django.db.models.fields.TextField')(null=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yati_api.User'], null=True)),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(related_name='logs', to=orm['yati_api.Unit'])),
            ('event', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'yati_api', ['UnitLog'])

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
        # Deleting model 'User'
        db.delete_table(u'yati_api_user')

        # Removing M2M table for field groups on 'User'
        db.delete_table(db.shorten_name(u'yati_api_user_groups'))

        # Removing M2M table for field user_permissions on 'User'
        db.delete_table(db.shorten_name(u'yati_api_user_user_permissions'))

        # Deleting model 'Project'
        db.delete_table(u'yati_api_project')

        # Deleting model 'Store'
        db.delete_table(u'yati_api_store')

        # Deleting model 'Unit'
        db.delete_table(u'yati_api_unit')

        # Deleting model 'StoreLog'
        db.delete_table(u'yati_api_storelog')

        # Deleting model 'UnitLog'
        db.delete_table(u'yati_api_unitlog')

        # Deleting model 'Location'
        db.delete_table(u'yati_api_location')

        # Deleting model 'Module'
        db.delete_table(u'yati_api_module')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
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
            'filename': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stores'", 'to': u"orm['yati_api.Project']"}),
            'sourcelanguage': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '10'}),
            'targetlanguage': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'po'", 'max_length': '100'})
        },
        u'yati_api.storelog': {
            'Meta': {'object_name': 'StoreLog'},
            'data': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'event': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'store': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'logs'", 'to': u"orm['yati_api.Store']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['yati_api.User']", 'null': 'True'})
        },
        u'yati_api.unit': {
            'Meta': {'ordering': "('store', 'index')", 'object_name': 'Unit'},
            'comments': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'fuzzy': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'msgid': ('dbarray.fields.TextArrayField', [], {'default': '[]', 'null': 'True'}),
            'msgstr': ('dbarray.fields.TextArrayField', [], {'default': '[]'}),
            'obsolete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'store': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'units'", 'to': u"orm['yati_api.Store']"})
        },
        u'yati_api.unitlog': {
            'Meta': {'object_name': 'UnitLog'},
            'data': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'event': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'logs'", 'to': u"orm['yati_api.Unit']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['yati_api.User']", 'null': 'True'})
        },
        u'yati_api.user': {
            'Meta': {'object_name': 'User'},
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'languages': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"})
        }
    }

    complete_apps = ['yati_api']