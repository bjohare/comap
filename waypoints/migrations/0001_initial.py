# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import waypoints.models
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
                ('created', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField(null=True)),
                ('the_geom', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
                ('visible', models.BooleanField(default=True)),
                ('route', models.ForeignKey(related_name='waypoints', to='routes.Route')),
            ],
            options={
                'db_table': 'waypoints',
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WaypointMedia',
            fields=[
                ('fid', models.AutoField(serialize=False, primary_key=True)),
                ('content_type', models.CharField(max_length=100)),
                ('filename', models.CharField(max_length=100)),
                ('size', models.IntegerField()),
                ('file', models.FileField(max_length=255, upload_to=waypoints.models.get_upload_path)),
                ('created', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField(blank=True)),
                ('waypoint', models.ForeignKey(related_name='waypoint_media', to='waypoints.Waypoint')),
            ],
            options={
                'db_table': 'waypoint_media',
                'managed': True,
            },
            bases=(models.Model,),
        ),
    ]
