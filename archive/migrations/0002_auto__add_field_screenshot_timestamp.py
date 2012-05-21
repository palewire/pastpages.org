# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Screenshot.timestamp'
        db.add_column('archive_screenshot', 'timestamp',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'Screenshot.timestamp'
        db.delete_column('archive_screenshot', 'timestamp')

    models = {
        'archive.screenshot': {
            'Meta': {'ordering': "('-update__start', 'site__name')", 'unique_together': "(('site', 'update'),)", 'object_name': 'Screenshot'},
            'crop': ('toolbox.thumbs.ImageWithThumbsField', [], {'max_length': '100', 'blank': 'True'}),
            'has_crop': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_html': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_image': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'html_archived': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'html_raw': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('toolbox.thumbs.ImageWithThumbsField', [], {'max_length': '100', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['archive.Site']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'update': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['archive.Update']"})
        },
        'archive.site': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Site'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'y_offset': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'})
        },
        'archive.update': {
            'Meta': {'ordering': "('-start',)", 'object_name': 'Update'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_tagged_items'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_items'", 'to': "orm['taggit.Tag']"})
        }
    }

    complete_apps = ['archive']