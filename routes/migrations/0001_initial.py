# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Route',
            fields=[
                ('fid', models.AutoField(serialize=False, primary_key=True)),
                ('created', models.DateTimeField()),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=65000)),
                ('image_file', models.CharField(max_length=100)),
                ('gpx_file', models.CharField(max_length=100)),
                ('the_geom', django.contrib.gis.db.models.fields.MultiLineStringField(srid=4326)),
                ('group', models.ForeignKey(related_name='route_groups', to='auth.Group')),
                ('user', models.ForeignKey(related_name='route_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'routes',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='TrackPoint',
            fields=[
                ('fid', models.AutoField(serialize=False, primary_key=True)),
                ('ele', models.DecimalField(null=True, max_digits=7, decimal_places=2)),
                ('time', models.DateTimeField(null=True)),
                ('the_geom', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('route', models.ForeignKey(related_name='track_points', to='routes.Route')),
            ],
            options={
                'db_table': 'track_points',
                'managed': True,
            },
        ),
    ]
