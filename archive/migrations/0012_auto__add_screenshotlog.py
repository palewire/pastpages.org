# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ScreenshotLog'
        db.create_table(u'archive_screenshotlog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('update', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['archive.Update'])),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['archive.Site'])),
            ('screenshot', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['archive.Screenshot'], null=True)),
            ('message_type', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('message', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'archive', ['ScreenshotLog'])

    def backwards(self, orm):
        # Deleting model 'ScreenshotLog'
        db.delete_table(u'archive_screenshotlog')

    models = {
        u'archive.champion': {
            'Meta': {'object_name': 'Champion'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'archive.screenshot': {
            'Meta': {'ordering': "('-update__start', 'site__sortable_name', 'site__name')", 'unique_together': "(('site', 'update'),)", 'object_name': 'Screenshot'},
            'crop': ('toolbox.thumbs.ImageWithThumbsField', [], {'max_length': '100', 'blank': 'True'}),
            'has_crop': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'has_html': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_image': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'html': ('urlarchivefield.fields.URLArchiveField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('toolbox.thumbs.ImageWithThumbsField', [], {'max_length': '100', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['archive.Site']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'update': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['archive.Update']"})
        },
        u'archive.screenshotlog': {
            'Meta': {'object_name': 'ScreenshotLog'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'message_type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'screenshot': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['archive.Screenshot']", 'null': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['archive.Site']"}),
            'update': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['archive.Update']"})
        },
        u'archive.site': {
            'Meta': {'ordering': "('sortable_name', 'name')", 'object_name': 'Site'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'display_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'has_html_screenshots': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hometown': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'on_the_homepage': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'sortable_name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20', 'db_index': 'True'}),
            'timezone': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'y_offset': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'})
        },
        u'archive.update': {
            'Meta': {'ordering': "('-start',)", 'object_name': 'Update'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['archive']