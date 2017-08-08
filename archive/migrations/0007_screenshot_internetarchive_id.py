# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0006_auto_20170808_0540'),
    ]

    operations = [
        migrations.AddField(
            model_name='screenshot',
            name='internetarchive_id',
            field=models.CharField(max_length=5000, blank=True),
        ),
    ]
