# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0009_auto_20170921_0346'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='screenshot',
            name='internetarchive_crop_url',
        ),
        migrations.RemoveField(
            model_name='screenshot',
            name='internetarchive_image_url',
        ),
    ]
