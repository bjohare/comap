# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Waypoints',
            fields=[
                ('fid', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255, blank=True)),
                ('description', models.CharField(max_length=1000, blank=True)),
                ('elevation', models.FloatField(null=True, blank=True)),
                ('date', models.CharField(max_length=19, blank=True)),
                ('the_geom', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
                ('image_path', models.CharField(max_length=500, blank=True)),
                ('owner', models.ForeignKey(related_name='waypoints', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'waypoints',
                'managed': True,
            },
            bases=(models.Model,),
        ),
    ]
