# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0005_auto_20170221_0543'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='screenshot',
            options={'ordering': ('-update__start', 'site__sortable_name', 'site__name'), 'get_latest_by': 'timestamp'},
        ),
        migrations.AddField(
            model_name='screenshot',
            name='internetarchive_url',
            field=models.CharField(max_length=5000, blank=True),
        ),
    ]
