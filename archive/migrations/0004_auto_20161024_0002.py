# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0003_auto_20161023_2210'),
    ]

    operations = [
        migrations.AlterField(
            model_name='site',
            name='has_internetarchive_mementos',
            field=models.BooleanField(default=False, verbose_name=b'has Internet Archive mementos'),
        ),
        migrations.AlterField(
            model_name='site',
            name='has_webcitation_mementos',
            field=models.BooleanField(default=False, verbose_name=b'has webcitation.org mementos'),
        ),
    ]
