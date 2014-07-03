# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Site.has_html_screenshots'
        db.add_column(u'archive_site', 'has_html_screenshots',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Deleting field 'Screenshot.html_archived'
        db.delete_column(u'archive_screenshot', 'html_archived')

        # Deleting field 'Screenshot.html_raw'
        db.delete_column(u'archive_screenshot', 'html_raw')

        # Adding field 'Screenshot.html'
        db.add_column(u'archive_screenshot', 'html',
                      self.gf('urlarchivefield.fields.URLArchiveField')(default='', max_length=100),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'Site.has_html_screenshots'
        db.delete_column(u'archive_site', 'has_html_screenshots')

        # Adding field 'Screenshot.html_archived'
        db.add_column(u'archive_screenshot', 'html_archived',
                      self.gf('django.db.models.fields.files.FileField')(default='', max_length=100, blank=True),
                      keep_default=False)

        # Adding field 'Screenshot.html_raw'
        db.add_column(u'archive_screenshot', 'html_raw',
                      self.gf('django.db.models.fields.files.FileField')(default='', max_length=100, blank=True),
                      keep_default=False)

        # Deleting field 'Screenshot.html'
        db.delete_column(u'archive_screenshot', 'html')

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
            'has_crop': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_html': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_image': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'html': ('urlarchivefield.fields.URLArchiveField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('toolbox.thumbs.ImageWithThumbsField', [], {'max_length': '100', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['archive.Site']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
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
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'}),
            'timezone': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'y_offset': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'})
        },
        u'archive.update': {
            'Meta': {'ordering': "('-start',)", 'object_name': 'Update'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'taggit_taggeditem_tagged_items'", 'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'taggit_taggeditem_items'", 'to': u"orm['taggit.Tag']"})
        }
    }

    complete_apps = ['archive']