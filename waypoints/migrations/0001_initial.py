# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('routes', '0003_auto_20150128_1753'),
    ]

    operations = [
        migrations.CreateModel(
            name='Waypoint',
            fields=[
                ('fid', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255, blank=True)),
                ('description', models.CharField(max_length=1000, blank=True)),
                ('elevation', models.FloatField(null=True, blank=True)),
                ('created', models.DateTimeField()),
                ('the_geom', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
                ('image_path', models.CharField(max_length=500, blank=True)),
                ('visible', models.BooleanField(default=True)),
                ('route', models.ForeignKey(related_name='wp_routes', to='routes.Route')),
            ],
            options={
                'db_table': 'waypoints',
                'managed': True,
            },
            bases=(models.Model,),
        ),
    ]
