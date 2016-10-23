# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Memento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('archive', models.CharField(db_index=True, max_length=1000, choices=[(b'archive.org', b'archive.org'), (b'webcitation.org', b'webcitation.org')])),
                ('url', models.URLField(blank=True)),
            ],
            options={
                'ordering': ('-update__start', 'site__sortable_name', 'site__name'),
            },
        ),
        migrations.AddField(
            model_name='site',
            name='has_internetarchive_mementos',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='site',
            name='has_webcitation_mementos',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='memento',
            name='site',
            field=models.ForeignKey(to='archive.Site'),
        ),
        migrations.AddField(
            model_name='memento',
            name='update',
            field=models.ForeignKey(to='archive.Update'),
        ),
        migrations.AlterUniqueTogether(
            name='memento',
            unique_together=set([('site', 'update')]),
        ),
        migrations.AlterIndexTogether(
            name='memento',
            index_together=set([('site', 'archive')]),
        ),
    ]
