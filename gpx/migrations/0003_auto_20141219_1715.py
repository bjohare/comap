# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gpx', '0002_auto_20141219_1621'),
    ]

    operations = [
        migrations.RenameField(
            model_name='route',
            old_name='time',
            new_name='created',
        ),
    ]
