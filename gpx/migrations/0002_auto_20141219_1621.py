# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('gpx', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='route',
            name='group',
            field=models.ForeignKey(related_name='route', to='auth.Group'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='route',
            name='user',
            field=models.ForeignKey(related_name='route', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
