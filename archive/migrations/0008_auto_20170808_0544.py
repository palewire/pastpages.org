# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0007_screenshot_internetarchive_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='screenshot',
            old_name='internetarchive_url',
            new_name='internetarchive_crop_url',
        ),
        migrations.AddField(
            model_name='screenshot',
            name='internetarchive_image_url',
            field=models.CharField(max_length=5000, blank=True),
        ),
    ]
