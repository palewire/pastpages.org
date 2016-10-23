# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0002_auto_20161023_1802'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='memento',
            unique_together=set([('site', 'update', 'archive')]),
        ),
    ]
